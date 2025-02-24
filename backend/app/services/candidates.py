from datetime import datetime
from typing import List, Optional
from fastapi import UploadFile, HTTPException
import os
import zipfile
import tempfile
from bson import ObjectId
from pathlib import Path
from app.core.config import settings
from app.core.mongodb import get_database, get_gridfs
from app.models.database import User
from app.models.database import serialize_candidate
from app.services.ai import extract_resume_info, analyze_resume
import logging
from io import BytesIO
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
import io

logger = logging.getLogger(__name__)

async def process_pdf_file(file_content: bytes, filename: str, job_id: str, created_by: User) -> dict:
    """
    Process a single PDF file and create a candidate record
    """
    try:
        # Save to temporary file for AI processing
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        try:
            # Extract basic info from resume using AI
            basic_info = await extract_resume_info(temp_path)
            
            # Analyze resume and compute score
            analysis_result = await analyze_resume(temp_path)

            # Get GridFS instance
            fs = await get_gridfs()
            
            # Store file in GridFS
            file_id = await fs.upload_from_stream(
                filename=filename,
                source=BytesIO(file_content),
                metadata={
                    "job_id": job_id,
                    "created_by": created_by.id,
                    "content_type": "application/pdf"
                }
            )
            
            db = await get_database()

            # Create candidate record
            candidate_id = ObjectId()
            candidate_data = {
                "_id": candidate_id,
                "id": str(candidate_id),
                "job_id": ObjectId(job_id),
                "name": basic_info.get("name", ""),
                "email": basic_info.get("email", ""),
                "phone": basic_info.get("phone"),
                "location": basic_info.get("location"),
                "resume_file_id": str(file_id),
                "skills": analysis_result.get("skills", {}),
                "resume_score": analysis_result.get("score", 0.0),
                "screening_score": None,
                "screening_summary": None,
                "created_by_id": ObjectId(created_by.id),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            logger.info(f"Storing candidate with resume file ID: {file_id}")
            await db.candidates.insert_one(candidate_data)
            
            # Increment the job's candidate count
            await db.jobs.update_one(
                {"_id": ObjectId(job_id)},
                {"$inc": {"total_candidates": 1}}
            )
            
            return serialize_candidate(candidate_data)
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
    except Exception as e:
        logger.error(f"Error processing PDF file: {str(e)}")
        raise

async def upload_resume(job_id: str, file: UploadFile, created_by: User) -> dict:
    """
    Process and upload a resume for a job. Handles both individual PDF files and ZIP files containing PDFs.
    """
    try:
        # Handle ZIP file
        if file.filename.lower().endswith('.zip'):
            # Create a temporary directory for ZIP contents
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save ZIP file
                zip_path = os.path.join(temp_dir, file.filename)
                content = await file.read()
                with open(zip_path, "wb") as buffer:
                    buffer.write(content)
                
                # Extract ZIP
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Process each PDF in the ZIP
                candidates = []
                for root, _, files in os.walk(temp_dir):
                    for filename in files:
                        if filename.lower().endswith('.pdf'):
                            # Read PDF content
                            pdf_path = os.path.join(root, filename)
                            with open(pdf_path, 'rb') as pdf_file:
                                pdf_content = pdf_file.read()
                            
                            # Process the PDF
                            candidate = await process_pdf_file(pdf_content, filename, job_id, created_by)
                            candidates.append(candidate)
                
                # Return the last processed candidate
                if candidates:
                    return candidates[-1]
                raise HTTPException(status_code=400, detail="No PDF files found in ZIP")
        
        # Handle individual PDF file
        elif file.filename.lower().endswith('.pdf'):
            content = await file.read()
            return await process_pdf_file(content, file.filename, job_id, created_by)
        
        else:
            raise HTTPException(status_code=400, detail="Only PDF or ZIP files are allowed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_resume_file(candidate_id: str) -> tuple[bytes, str]:
    """
    Retrieve a candidate's resume file from GridFS
    Returns tuple of (file_content, filename)
    """
    try:
        db = await get_database()

        # Get candidate to find file ID
        candidate = await db.candidates.find_one({"_id": ObjectId(candidate_id)})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        file_id = candidate.get("resume_file_id")
        if not file_id:
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        # Get file from GridFS
        try:
            fs = await get_gridfs()
            grid_out = await fs.open_download_stream(ObjectId(file_id))
            content = await grid_out.read()
            filename = grid_out.filename
            return content, filename
        except Exception as e:
            logger.error(f"Error reading file from GridFS: {str(e)}")
            raise HTTPException(status_code=404, detail="Resume file not found in GridFS")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving resume file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_candidates(job_id: str, skip: int = 0, limit: int = 10) -> List[dict]:
    """
    Get all candidates for a job
    """
    try:
        logger.info(f"Fetching candidates for job_id: {job_id}")
        
        # Log the query we're about to make
        logger.info(f"Querying candidates with job_id: {ObjectId(job_id)}")
        
        db = await get_database()

        cursor = db.candidates.find({"job_id": ObjectId(job_id)}).skip(skip).limit(limit)
        candidates = await cursor.to_list(length=limit)
        
        logger.info(f"Found {len(candidates)} candidates")
        
        # Log each candidate before serialization
        serialized_candidates = []
        for candidate in candidates:
            try:
                serialized = serialize_candidate(candidate)
                serialized_candidates.append(serialized)
                logger.info(f"Successfully serialized candidate: {candidate['_id']}")
            except Exception as e:
                logger.error(f"Error serializing candidate {candidate.get('_id', 'unknown')}: {str(e)}")
                raise
        
        return serialized_candidates
    except Exception as e:
        logger.error(f"Error fetching candidates: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching candidates: {str(e)}")

async def get_candidate(job_id: str, candidate_id: str) -> Optional[dict]:
    """
    Get a specific candidate
    """
    try:
        db = await get_database()

        candidate_data = await db.candidates.find_one({
            "_id": ObjectId(candidate_id),
            "job_id": ObjectId(job_id)
        })
        if candidate_data:
            return serialize_candidate(candidate_data)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching candidate: {str(e)}")

async def update_candidate_info(
    candidate_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    location: Optional[str] = None,
    skills: Optional[dict] = None,
    resume_score: Optional[float] = None,
) -> Optional[dict]:
    """
    Update candidate information after AI processing
    """
    try:
        db = await get_database()

        update_data = {
            "updated_at": datetime.utcnow()
        }
        if name:
            update_data["name"] = name
        if email:
            update_data["email"] = email
        if phone:
            update_data["phone"] = phone
        if location:
            update_data["location"] = location
        if skills:
            update_data["skills"] = skills
        if resume_score is not None:
            update_data["resume_score"] = resume_score

        result = await db.candidates.find_one_and_update(
            {"_id": ObjectId(candidate_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            return serialize_candidate(result)
        return None
    except Exception as e:
        logger.error(f"Error updating candidate: {str(e)}", exc_info=True)
        raise

async def delete_candidate(candidate_id: str):
    """
    Delete a candidate and their resume file
    """
    try:
        db = await get_database()

        # Get candidate to find file ID
        candidate = await db.candidates.find_one({"_id": ObjectId(candidate_id)})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Delete resume file from GridFS if it exists
        file_id = candidate.get("resume_file_id")
        if file_id:
            try:
                fs = await get_gridfs()
                await fs.delete(ObjectId(file_id))
            except Exception as e:
                logger.error(f"Error deleting file from GridFS: {str(e)}")
        
        # Delete candidate record
        result = await db.candidates.delete_one({"_id": ObjectId(candidate_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Decrement the job's candidate count
        await db.jobs.update_one(
            {"_id": candidate["job_id"]},
            {"$inc": {"total_candidates": -1}}
        )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting candidate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def migrate_candidates_to_gridfs():
    """Migrate candidates with resume_path to GridFS storage"""
    logger.info("Starting candidate migration to GridFS")
    try:
        db = await get_database()

        cursor = db.candidates.find({"resume_path": {"$exists": True}})
        candidates = await cursor.to_list(length=None)
        
        for candidate in candidates:
            try:
                resume_path = candidate.get("resume_path")
                if not resume_path or not os.path.exists(resume_path):
                    continue
                    
                # Read the file
                with open(resume_path, 'rb') as file:
                    content = file.read()
                    
                # Upload to GridFS
                async for fs in get_gridfs():
                    file_id = await fs.upload_from_stream(
                        filename=os.path.basename(resume_path),
                        source=BytesIO(content),
                        metadata={
                            "job_id": str(candidate["job_id"]),
                            "created_by": str(candidate["created_by_id"]),
                            "content_type": "application/pdf"
                        }
                    )
                    
                    # Update candidate record
                    await db.candidates.update_one(
                        {"_id": candidate["_id"]},
                        {
                            "$set": {"resume_file_id": str(file_id)},
                            "$unset": {"resume_path": ""}
                        }
                    )
                    
                    logger.info(f"Migrated resume for candidate {candidate['_id']} to GridFS")
                    
            except Exception as e:
                logger.error(f"Error migrating candidate {candidate['_id']}: {str(e)}")
                continue
                
        logger.info("Completed candidate migration to GridFS")
    except Exception as e:
        logger.error(f"Error during candidate migration: {str(e)}", exc_info=True)
        raise

# Update the serialize_candidate function to handle both old and new fields
def serialize_candidate(candidate: dict) -> dict:
    """Convert MongoDB candidate document to JSON-serializable format"""
    try:
        # Get either resume_file_id or resume_path
        resume_identifier = candidate.get("resume_file_id", candidate.get("resume_path", ""))
        
        return {
            "id": str(candidate["_id"]),
            "job_id": str(candidate["job_id"]),
            "name": candidate["name"],
            "email": candidate["email"],
            "phone": candidate["phone"],
            "location": candidate["location"],
            "resume_file_id": resume_identifier,  # Use whichever we found
            "skills": candidate["skills"],
            "resume_score": candidate["resume_score"],
            "screening_score": candidate["screening_score"],
            "screening_summary": candidate["screening_summary"],
            "created_by_id": str(candidate["created_by_id"]) if candidate.get("created_by_id") else None,
            "created_at": candidate["created_at"].isoformat(),
            "updated_at": candidate["updated_at"].isoformat()
        }
    except Exception as e:
        logger.error(f"Error serializing candidate {candidate.get('_id', 'unknown')}: {str(e)}")
        logger.error(f"Candidate data: {candidate}")
        raise 

async def create_candidate(job_id: str, file: UploadFile) -> dict:
    """Create a new candidate with resume upload."""
    try:
        # Validate job_id
        if not ObjectId.is_valid(job_id):
            raise HTTPException(status_code=400, detail="Invalid job ID")

        # Read file content
        content = await file.read()

        # Get database connection
        db = await get_database()

        # Create GridFS bucket
        fs = AsyncIOMotorGridFSBucket(db)

        # Upload file to GridFS
        file_id = await fs.upload_from_stream(
            file.filename,
            io.BytesIO(content),
            metadata={"job_id": job_id}
        )

        # Analyze resume
        resume_info = await extract_resume_info(io.BytesIO(content))
        analysis_result = await analyze_resume(io.BytesIO(content))

        # Create candidate document
        candidate = {
            "job_id": ObjectId(job_id),
            "name": resume_info.get("name", "Unknown"),
            "email": resume_info.get("email", ""),
            "phone": resume_info.get("phone"),
            "location": resume_info.get("location"),
            "resume_file_id": file_id,
            "skills": analysis_result.get("skills", {}),
            "resume_score": analysis_result.get("score", 0),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await db.candidates.insert_one(candidate)

        # Update job's candidate count
        await db.jobs.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$inc": {
                    "total_candidates": 1,
                    "resume_screened": 1
                }
            }
        )

        # Return created candidate
        candidate["id"] = str(result.inserted_id)
        return serialize_candidate(candidate)

    except Exception as e:
        # Clean up GridFS file if it was uploaded
        if 'file_id' in locals():
            try:
                db = get_database()
                fs = AsyncIOMotorGridFSBucket(db)
                await fs.delete(file_id)
            except Exception as cleanup_error:
                print(f"Error cleaning up GridFS file: {cleanup_error}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create candidate: {str(e)}"
        ) 