#!/usr/bin/env python3
"""
Script to directly update a candidate's notice period in the database.
This bypasses the API and Ultravox integration for quick testing.
"""
import asyncio
import argparse
import logging
import sys
import os
from pathlib import Path
from datetime import datetime, UTC
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Default values
DEFAULT_CANDIDATE_ID = "67bd8328b318f42cb1aa9ed2"
DEFAULT_MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DEFAULT_MONGODB_DB = os.getenv("MONGODB_DB_NAME", "recruitment")

async def update_candidate_notice_period(candidate_id, notice_period, current_compensation=None, 
                               expected_compensation=None, screening_score=85):
    """
    Directly update a candidate's notice period in the database
    """
    client = None
    try:
        mongodb_url = os.getenv("MONGODB_URL")
        db_name = os.getenv("MONGODB_DB_NAME")
        
        logger.info(f"Connecting to MongoDB at {mongodb_url}")
        client = AsyncIOMotorClient(mongodb_url)
        db = client[db_name]
        
        # Check if the candidate exists
        candidate = await db.candidates.find_one({"_id": ObjectId(candidate_id)})
        if not candidate:
            logger.error(f"Candidate with ID {candidate_id} not found")
            return False
        
        logger.info(f"Found candidate: {candidate['name']} (ID: {candidate_id})")
        
        # Build update object
        update_data = {
            "screening_in_progress": False,
            "screening_score": screening_score,
            "screening_summary": f"The candidate has a notice period of {notice_period}.",
            "notice_period": notice_period,
            "updated_at": datetime.now(UTC)
        }
        
        # Add optional fields if provided
        if current_compensation:
            update_data["current_compensation"] = current_compensation
        
        if expected_compensation:
            update_data["expected_compensation"] = expected_compensation
        
        # Update the candidate
        result = await db.candidates.update_one(
            {"_id": ObjectId(candidate_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 1:
            logger.info(f"✅ Successfully updated candidate {candidate_id}")
            
            # Also update the job's phone_screened count
            job_id = candidate.get("job_id")
            if job_id:
                await db.jobs.update_one(
                    {"_id": job_id},
                    {
                        "$inc": {"phone_screened": 1},
                        "$set": {"updated_at": datetime.now(UTC)}
                    }
                )
                logger.info(f"✅ Updated job phone_screened count")
            
            # Get updated candidate data
            updated_candidate = await db.candidates.find_one({"_id": ObjectId(candidate_id)})
            logger.info(f"Updated candidate data:")
            logger.info(f"Notice Period: {updated_candidate.get('notice_period')}")
            logger.info(f"Screening Score: {updated_candidate.get('screening_score')}")
            logger.info(f"Current Compensation: {updated_candidate.get('current_compensation')}")
            logger.info(f"Expected Compensation: {updated_candidate.get('expected_compensation')}")
            logger.info(f"Screening In Progress: {updated_candidate.get('screening_in_progress')}")
            
            return True
        else:
            logger.error(f"❌ Failed to update candidate {candidate_id}")
            return False
    except Exception as e:
        logger.error(f"Error updating candidate: {str(e)}")
        raise
    finally:
        # Close MongoDB connection
        if client:
            client.close()

def main():
    parser = argparse.ArgumentParser(description="Update candidate notice period directly in database")
    parser.add_argument("--candidate-id", default=DEFAULT_CANDIDATE_ID, help="Candidate ID to update")
    parser.add_argument("--notice-period", default="2 months", help="Notice period value to set")
    parser.add_argument("--current-compensation", help="Current compensation value (optional)")
    parser.add_argument("--expected-compensation", help="Expected compensation value (optional)")
    parser.add_argument("--screening-score", type=float, default=85.0, help="Screening score (0-100)")
    
    args = parser.parse_args()
    
    asyncio.run(update_candidate_notice_period(
        candidate_id=args.candidate_id,
        notice_period=args.notice_period,
        current_compensation=args.current_compensation,
        expected_compensation=args.expected_compensation,
        screening_score=args.screening_score
    ))

if __name__ == "__main__":
    main() 