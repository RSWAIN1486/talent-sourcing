from datetime import datetime, UTC
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
from app.services.ai import extract_resume_info, analyze_resume, analyze_call_transcript
import logging
from io import BytesIO
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
import io
import asyncio
import httpx
import re
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import json
from twilio.twiml.voice_response import Connect, VoiceResponse, Say, Stream

logger = logging.getLogger(__name__)

# Helper function for phone number formatting
def format_phone_number(phone: str) -> str:
    """
    Format a phone number to E.164 format for Twilio
    """
    # Remove any non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # If the number doesn't start with a country code, add +1 (US)
    if not phone.startswith('+'):
        if len(digits_only) == 10:  # US number without country code
            return f"+1{digits_only}"
        elif len(digits_only) == 11 and digits_only.startswith('1'):  # US number with 1 prefix
            return f"+{digits_only}"
        else:
            # For other cases, just add + prefix as a fallback
            return f"+{digits_only}"
    
    return phone  # Already in E.164 format

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
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
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
        
        # Get cursor and apply pagination
        cursor = db.candidates.find({"job_id": ObjectId(job_id)})
        cursor = cursor.skip(skip).limit(limit)
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
    update_fields: Optional[dict] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    location: Optional[str] = None,
    skills: Optional[dict] = None,
    resume_score: Optional[float] = None,
) -> Optional[dict]:
    """
    Update candidate information after AI processing
    
    Args:
        candidate_id: The ID of the candidate to update
        update_fields: Dictionary of fields to update (alternative to individual parameters)
        name: Optional name to update
        email: Optional email to update
        phone: Optional phone to update
        location: Optional location to update
        skills: Optional skills dictionary to update
        resume_score: Optional resume score to update
        
    Returns:
        Updated candidate data or None if not found
    """
    try:
        db = await get_database()

        update_data = {
            "updated_at": datetime.now(UTC)
        }
        
        # If update_fields dictionary is provided, use it
        if update_fields and isinstance(update_fields, dict):
            for key, value in update_fields.items():
                update_data[key] = value
        else:
            # Otherwise use individual parameters
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
            "updated_at": candidate["updated_at"].isoformat(),
            "screening_in_progress": candidate.get("screening_in_progress", False),
            "current_compensation": candidate.get("current_compensation", None),
            "expected_compensation": candidate.get("expected_compensation", None),
            "notice_period": candidate.get("notice_period", None),
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

        # Get GridFS instance properly
        fs = await get_gridfs()

        # Upload file to GridFS
        file_id = await fs.upload_from_stream(
            file.filename,
            io.BytesIO(content),
            metadata={"job_id": job_id}
        )

        try:
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
                "resume_file_id": str(file_id),  # Convert ObjectId to string
                "skills": analysis_result.get("skills", {}),
                "resume_score": analysis_result.get("score", 0),
                "screening_score": None,
                "screening_summary": None,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            }

            result = await db.candidates.insert_one(candidate)
            candidate["_id"] = result.inserted_id

            # Update job's statistics
            await db.jobs.update_one(
                {"_id": ObjectId(job_id)},
                {
                    "$inc": {
                        "total_candidates": 1,
                        "resume_screened": 1
                    },
                    "$set": {
                        "updated_at": datetime.now(UTC)
                    }
                }
            )

            # Return created candidate
            return serialize_candidate(candidate)

        except Exception as inner_e:
            # If anything fails after file upload, clean up the uploaded file
            try:
                await fs.delete(file_id)
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up GridFS file: {cleanup_error}")
            raise inner_e

    except Exception as e:
        logger.error(f"Failed to create candidate: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create candidate: {str(e)}"
        ) 

async def voice_screen_candidate(job_id: str, candidate_id: str, current_user: User) -> dict:
    """
    Initiate a voice screening call to a candidate using Ultravox and Twilio
    """
    try:
        logger.info(f"Initiating voice screening for candidate: {candidate_id}")
        
        # Get database connection
        db = await get_database()
        
        # Get candidate details
        candidate = await db.candidates.find_one({"_id": ObjectId(candidate_id)})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Get job details
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if candidate has a phone number
        if not candidate.get("phone"):
            raise HTTPException(status_code=400, detail="Candidate does not have a phone number")
        
        # Format phone number to E.164 format for Twilio
        phone = format_phone_number(candidate.get("phone"))
        if not phone:
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        # Create a system prompt based on the job details
        system_prompt = f"""
        You are an AI voice assistant conducting a screening interview for a job. 
        
        Job Title: {job.get('title')}
        Job Description: {job.get('description')}
        
        Candidate Name: {candidate.get('name')}
        
        Your task is to conduct a brief less than 3 minute screening interview to assess the candidate. 
        
        Follow this structure:
        1. Greeting: Introduce yourself as an AI assistant for [Company Name] and confirm you're speaking with {candidate.get('name')}
        2. Initial Check: Ask if they are currently looking for job opportunities
        3. Notice Period: Ask about their current notice period
        4. Compensation: Ask about their current and expected compensation
        5. Technical Assessment: Ask if they have any experience with the technologies used in the job description.
        6. Closing: Thank them for their time and explain the next steps in the process
        
        Be professional, friendly, and concise. Listen to their answers and respond appropriately.
        After the call, provide a summary of the candidate's responses and a screening score from 0 to 100.
        """
        
        # Initialize Twilio client
        try:
            twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize Twilio client: {str(e)}")
        
        # Construct the webhook URL for call completion
        webhook_url = f"{settings.WEBHOOK_BASE_URL}{settings.API_V1_STR}/candidates/callback/call-complete"
        
        # Update the candidate's record to show a screening is in progress
        await db.candidates.update_one(
            {"_id": ObjectId(candidate_id)},
            {
                "$set": {
                    "screening_in_progress": True,
                    "updated_at": datetime.now(UTC)
                }
            }
        )
        
        # Use mock implementation by default or if Ultravox API is unavailable
        use_mock = False
        agent_id = f"mock_agent_{candidate_id}"
        
        # Try to use Ultravox if configured
        if settings.ULTRAVOX_API_KEY and settings.ULTRAVOX_API_KEY != "mock":
            try:
                # Create agent in Ultravox
                async with httpx.AsyncClient() as client:
                    try:
                        # Log the API request details
                        ultravox_payload = {
                            "systemPrompt": system_prompt,
                            "temperature": 0.7,
                            "model": "fixie-ai/ultravox",
                            "voice": "ebae2397-0ba1-4222-9d5b-5313ddeb04b5",
                            "medium": {
                                "twilio": {}
                            },
                            "recordingEnabled": True,
                            "firstSpeaker": "FIRST_SPEAKER_USER"
                        }
                        
                        logger.info(f"Making Ultravox API call to: {settings.ULTRAVOX_API_BASE_URL}/api/calls")
                        logger.info(f"Request payload: {json.dumps(ultravox_payload)}")
                        
                        ultravox_response = await client.post(
                            f"{settings.ULTRAVOX_API_BASE_URL}/api/calls",
                            headers={
                                "X-API-Key": settings.ULTRAVOX_API_KEY,
                                "Content-Type": "application/json"
                            },
                            json=ultravox_payload,
                            timeout=30.0
                        )
                        
                        # Log the response status
                        logger.info(f"Ultravox API response status: {ultravox_response.status_code}")
                        
                        # Only proceed if we get a successful response
                        if ultravox_response.status_code in (200, 201):  # Check for both 200 OK and 201 Created
                            try:
                                ultravox_data = ultravox_response.json()
                                logger.info(f"Ultravox API response body: {json.dumps(ultravox_data)}")
                                
                                if ultravox_data and "callId" in ultravox_data:  # API returns callId, not id
                                    agent_id = ultravox_data.get("callId")
                                    join_url = ultravox_data.get("joinUrl")
                                    use_mock = False
                                    logger.info(f"Created Ultravox call: {agent_id}, join URL: {join_url}")
                                else:
                                    logger.warning("Ultravox API returned success but no callId. Falling back to mock implementation.")
                                    use_mock = True
                            except json.JSONDecodeError:
                                response_text = await ultravox_response.text()
                                logger.error(f"Failed to parse JSON response: {response_text}")
                                use_mock = True
                        else:
                            response_text = await ultravox_response.text()
                            logger.warning(f"Ultravox API returned status code {ultravox_response.status_code}. Response: {response_text}. Falling back to mock implementation.")
                            use_mock = True
                    except (httpx.HTTPError, json.JSONDecodeError) as e:
                        logger.warning(f"Ultravox API error: {str(e)}. Falling back to mock implementation.")
                        use_mock = True
            except Exception as e:
                logger.warning(f"Error connecting to Ultravox: {str(e)}. Falling back to mock implementation.")
                use_mock = True
        
        # Use mock implementation if needed
        if use_mock:
            logger.info("Using mock Ultravox integration")
            
            # Create a simple TwiML for testing
            twiml = f"""
            <Response>
                <Say>Hello {candidate.get('name')}, this is an AI assistant calling from a recruitment agency.</Say>
                <Pause length="1"/>
                <Say>I'm calling about the {job.get('title')} position. Would you be interested in discussing this opportunity?</Say>
                <Pause length="2"/>
                <Say>Thank you. What is your current notice period at your job?</Say>
                <Pause length="2"/>
                <Say>And what is your current compensation package?</Say>
                <Pause length="2"/>
                <Say>What are your salary expectations for this new role?</Say>
                <Pause length="2"/>
                <Say>Thank you for your time. Someone from our team will follow up with you shortly about next steps.</Say>
            </Response>
            """
            
            # Make the Twilio call with TwiML
            try:
                call = twilio_client.calls.create(
                    to=phone,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    twiml=twiml,
                    status_callback=webhook_url,
                    status_callback_event=['completed'],
                    status_callback_method='POST'
                )
                
                call_id = call.sid
                logger.info(f"Initiated Twilio call with mock TwiML: {call_id}")
            except TwilioRestException as e:
                logger.error(f"Twilio error: {str(e)}")
                # Update the candidate's record to show screening is no longer in progress
                await db.candidates.update_one(
                    {"_id": ObjectId(candidate_id)},
                    {
                        "$set": {
                            "screening_in_progress": False,
                            "updated_at": datetime.now(UTC)
                        }
                    }
                )
                raise HTTPException(status_code=500, detail=f"Twilio error: {str(e)}")
        else:
            # Make the Twilio call with Ultravox
            try:

                response = VoiceResponse()
                connect = Connect()
                connect.stream(url=join_url)
                response.append(connect)
                response.say(
                    'This TwiML instruction is unreachable unless the Stream is ended by your WebSocket server.'
                )

                print(response)
                call =  twilio_client.calls.create(
                        to=phone,
                        from_=settings.TWILIO_PHONE_NUMBER,
                        twiml=response,
                        status_callback=webhook_url,
                        status_callback_event=['completed'],
                        status_callback_method='POST'
                    )
                
                call_id = call.sid
                logger.info(f"Initiated Twilio call with Ultravox: {call_id}")
            except TwilioRestException as e:
                logger.error(f"Twilio error: {str(e)}")
                # Update the candidate's record to show screening is no longer in progress
                await db.candidates.update_one(
                    {"_id": ObjectId(candidate_id)},
                    {
                        "$set": {
                            "screening_in_progress": False,
                            "updated_at": datetime.now(UTC)
                        }
                    }
                )
                raise HTTPException(status_code=500, detail=f"Twilio error: {str(e)}")
        
        # Store the call info
        await db.call_sessions.insert_one({
            "call_id": call_id,  # This is the Twilio call SID
            "ultravox_call_id": agent_id if not use_mock else None,  # This is the Ultravox call ID
            "candidate_id": ObjectId(candidate_id),
            "job_id": ObjectId(job_id),
            "phone_number": phone,
            "system_prompt": system_prompt,
            "status": "initiated",
            "created_by_id": ObjectId(current_user.id if hasattr(current_user, 'id') else current_user.get('id')),
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        })
        
        return {
            "call_id": call_id,
            "ultravox_call_id": agent_id if not use_mock else None,
            "status": "initiated"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in voice_screen_candidate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_call_results(call_data: dict) -> dict:
    """Process call results from Ultravox/Twilio"""
    try:
        logger.info(f"Processing call results: {call_data}")
        
        # Get database connection
        db = await get_database()
        
        # Get call ID from Twilio webhook or Ultravox callback
        # The structure will differ based on which service sends the webhook
        # We'll check for both possibilities
        
        call_id = call_data.get("CallSid") or call_data.get("call_id")
        if not call_id:
            logger.error("No call ID found in webhook data")
            return {"status": "error", "message": "No call ID found in webhook data"}
        
        # Find the call session
        call_session = await db.call_sessions.find_one({"call_id": call_id})
        if not call_session:
            logger.error(f"Call session not found for call_id: {call_id}")
            return {"status": "error", "message": f"Call session not found for call_id: {call_id}"}
        
        candidate_id = call_session.get("candidate_id")
        ultravox_call_id = call_session.get("ultravox_call_id") or call_session.get("agent_id")
        
        # For testing: Generate mock data if using mock Ultravox integration
        if not ultravox_call_id or (isinstance(ultravox_call_id, str) and ultravox_call_id.startswith("mock_agent_")):
            logger.info("Using mock call results")
            
            # Generate mock call results
            transcript = "AI: Hello, this is an AI assistant calling from a recruitment agency.\nCandidate: Hi, yes this is me.\nAI: I'm calling about the Software Engineer position. Would you be interested in discussing this opportunity?\nCandidate: Yes, I'm interested.\nAI: Thank you. What is your current notice period at your job?\nCandidate: I need to give 30 days notice.\nAI: And what is your current compensation package?\nCandidate: I'm currently making 90,000 per year.\nAI: What are your salary expectations for this new role?\nCandidate: I'm looking for around 110,000.\nAI: Thank you for your time. Someone from our team will follow up with you shortly about next steps."
            
            screening_score = 85
            notice_period = "30 days"
            current_compensation = "$90,000"
            expected_compensation = "$110,000"
            screening_summary = "The candidate is interested in the position. They have a 30-day notice period at their current job. Currently making $90,000 and expecting $110,000 for the new role."
        else:
            # Get call transcript and analysis from Ultravox
            async with httpx.AsyncClient() as client:
                try:
                    ultravox_response = await client.get(
                        f"{settings.ULTRAVOX_API_BASE_URL}/api/calls/{ultravox_call_id}",
                        headers={
                            "X-API-Key": settings.ULTRAVOX_API_KEY,
                            "Content-Type": "application/json"
                        },
                        timeout=30
                    )
                    
                    ultravox_response.raise_for_status()
                    call_details = ultravox_response.json()
                    
                    # Get transcript - update endpoint to list call messages
                    transcript_response = await client.get(
                        f"{settings.ULTRAVOX_API_BASE_URL}/api/calls/{ultravox_call_id}/messages",
                        headers={
                            "X-API-Key": settings.ULTRAVOX_API_KEY,
                            "Content-Type": "application/json"
                        },
                        timeout=30
                    )
                    
                    transcript_response.raise_for_status()
                    messages_data = transcript_response.json()
                    
                    # Extract transcript from messages
                    transcript = ""
                    for message in messages_data.get("messages", []):
                        role = "AI" if message.get("role") == "MESSAGE_ROLE_AGENT" else "User"
                        text = message.get("text", "")
                        if text:
                            transcript += f"{role}: {text}\n"
                    
                    # Get summary from Ultravox
                    screening_summary = call_details.get("summary", "No summary available")
                    
                    # Use OpenAI to analyze the summary and extract structured data
                    analysis_results = await analyze_call_transcript(screening_summary)
                except Exception as e:
                    logger.error(f"Error extracting details: {e}")
                            # Update the candidate with the call results
        await db.candidates.update_one(
            {"_id": ObjectId(candidate_id)},
            {
                "$set": {
                        "screening_in_progress": False,
                        "call_transcript": transcript,  # Save the full transcript
                        "screening_score": analysis_results.get("screening_score", 0),
                        "screening_summary": screening_summary,  # Use Ultravox's summary
                        "notice_period": analysis_results.get("notice_period", "Not specified"),
                        "current_compensation": analysis_results.get("current_compensation", "Not specified"),
                        "expected_compensation": analysis_results.get("expected_compensation", "Not specified"),
                        "updated_at": datetime.now(UTC)
                }
            }
        )
        
        # Update job statistics
        job_id = call_session.get("job_id")
        await db.jobs.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$inc": {
                    "phone_screened": 1
                },
                "$set": {
                    "updated_at": datetime.now(UTC)
                }
            }
        )
        
        # Update call session status
        await db.call_sessions.update_one(
            {"call_id": call_id},
            {
                "$set": {
                    "status": "completed",
                    "results": {
                        "screening_score": analysis_results.get("screening_score", 0),
                        "screening_summary": screening_summary,
                        "notice_period": analysis_results.get("notice_period", "Not specified"),
                        "current_compensation": analysis_results.get("current_compensation", "Not specified"),
                        "expected_compensation": analysis_results.get("expected_compensation", "Not specified")
                    },
                    "updated_at": datetime.now(UTC)
                }
            }
        )
        
        return {
            "success": True,
            "call_id": call_id,
            "status": "completed",
            "screening_score": analysis_results.get("screening_score", 0)
        }
    except Exception as e:
        logger.error(f"Error processing call results: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)} 