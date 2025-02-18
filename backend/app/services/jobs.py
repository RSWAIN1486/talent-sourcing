from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.core.mongodb import get_database
from app.models.database import create_job, serialize_job
import logging

logger = logging.getLogger(__name__)

async def create_job(
    title: str,
    description: str,
    responsibilities: str,
    requirements: str,
    created_by: dict
) -> dict:
    """Create a new job posting"""
    try:
        logger.info(f"Creating job with title: {title}")
        logger.info(f"Created by user: {created_by}")
        
        db = get_database()
        logger.info("Got database connection")
        
        # Create job document
        try:
            job = {
                "_id": ObjectId(),
                "title": title,
                "description": description,
                "responsibilities": responsibilities,
                "requirements": requirements,
                "total_candidates": 0,
                "resume_screened": 0,
                "phone_screened": 0,
                "created_by_id": ObjectId(created_by["_id"]),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            logger.info(f"Created job document: {job}")
        except Exception as e:
            logger.error(f"Error creating job document: {str(e)}", exc_info=True)
            raise
        
        # Insert into database
        try:
            result = await db.jobs.insert_one(job)
            logger.info(f"Inserted job into database. Result: {result.inserted_id}")
            job["_id"] = result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting job into database: {str(e)}", exc_info=True)
            raise
        
        # Serialize and return
        try:
            serialized_job = serialize_job(job)
            logger.info(f"Serialized job: {serialized_job}")
            return serialized_job
        except Exception as e:
            logger.error(f"Error serializing job: {str(e)}", exc_info=True)
            raise
            
    except Exception as e:
        logger.error(f"Unexpected error in create_job service: {str(e)}", exc_info=True)
        raise

async def get_job(job_id: str) -> Optional[dict]:
    db = get_database()
    job_data = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if job_data:
        return serialize_job(job_data)
    return None

async def get_jobs(skip: int = 0, limit: int = 10) -> List[dict]:
    db = get_database()
    cursor = db.jobs.find().skip(skip).limit(limit)
    jobs = await cursor.to_list(length=limit)
    return [serialize_job(job) for job in jobs]

async def update_job(
    job_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    responsibilities: Optional[str] = None,
    requirements: Optional[str] = None
) -> Optional[dict]:
    db = get_database()
    update_data = {
        "updated_at": datetime.utcnow()
    }
    if title:
        update_data["title"] = title
    if description:
        update_data["description"] = description
    if responsibilities:
        update_data["responsibilities"] = responsibilities
    if requirements:
        update_data["requirements"] = requirements

    result = await db.jobs.find_one_and_update(
        {"_id": ObjectId(job_id)},
        {"$set": update_data},
        return_document=True
    )
    if result:
        return serialize_job(result)
    return None

async def delete_job(job_id: str) -> bool:
    db = get_database()
    result = await db.jobs.delete_one({"_id": ObjectId(job_id)})
    return result.deleted_count > 0

async def increment_job_stats(
    job_id: str,
    total_candidates: int = 0,
    resume_screened: int = 0,
    phone_screened: int = 0
) -> Optional[dict]:
    """
    Increment job statistics with the new counts
    """
    try:
        db = get_database()
        logger.info(f"Incrementing stats for job {job_id}: total={total_candidates}, resume={resume_screened}, phone={phone_screened}")
        
        update_data = {
            "updated_at": datetime.utcnow()
        }
        if total_candidates:
            update_data["total_candidates"] = total_candidates
        if resume_screened:
            update_data["resume_screened"] = resume_screened
        if phone_screened:
            update_data["phone_screened"] = phone_screened

        result = await db.jobs.find_one_and_update(
            {"_id": ObjectId(job_id)},
            {"$inc": update_data},
            return_document=True
        )
        if result:
            logger.info(f"Successfully updated job stats: {result}")
            return serialize_job(result)
        return None
    except Exception as e:
        logger.error(f"Error incrementing job stats: {str(e)}")
        raise

async def sync_job_candidates_count(job_id: str) -> Optional[dict]:
    """
    Sync the job's candidate counts with the actual numbers in the database
    """
    try:
        db = get_database()
        logger.info(f"Starting sync for job {job_id}")
        
        # Count actual candidates
        total_candidates = await db.candidates.count_documents({"job_id": ObjectId(job_id)})
        logger.info(f"Total candidates: {total_candidates}")
        
        # Count resume screened candidates (those with a resume score)
        resume_screened = await db.candidates.count_documents({
            "job_id": ObjectId(job_id),
            "resume_score": {"$ne": None}
        })
        logger.info(f"Resume screened candidates: {resume_screened}")
        
        # Count phone screened candidates (those with a screening score)
        phone_screened = await db.candidates.count_documents({
            "job_id": ObjectId(job_id),
            "screening_score": {"$ne": None}
        })
        logger.info(f"Phone screened candidates: {phone_screened}")
        
        # Update job with actual counts
        result = await db.jobs.find_one_and_update(
            {"_id": ObjectId(job_id)},
            {"$set": {
                "total_candidates": total_candidates,
                "resume_screened": resume_screened,
                "phone_screened": phone_screened,
                "updated_at": datetime.utcnow()
            }},
            return_document=True
        )
        
        if result:
            logger.info(f"Successfully updated job with new counts: {result}")
            return serialize_job(result)
            
        logger.error(f"Job {job_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error syncing job candidates count: {str(e)}", exc_info=True)
        raise

async def migrate_job_fields() -> None:
    """
    Migrate existing jobs to use new field names
    """
    try:
        db = get_database()
        logger.info("Starting job field migration")
        
        # Update all jobs to use new field names
        result = await db.jobs.update_many(
            {
                "$or": [
                    {"screened_candidates": {"$exists": True}},
                    {"called_candidates": {"$exists": True}}
                ]
            },
            [
                {
                    "$set": {
                        "resume_screened": {"$ifNull": ["$screened_candidates", 0]},
                        "phone_screened": {"$ifNull": ["$called_candidates", 0]}
                    }
                },
                {
                    "$unset": ["screened_candidates", "called_candidates"]
                }
            ]
        )
        
        logger.info(f"Migration complete. Modified {result.modified_count} jobs")
    except Exception as e:
        logger.error(f"Error migrating job fields: {str(e)}", exc_info=True)
        raise 