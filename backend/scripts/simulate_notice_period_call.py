#!/usr/bin/env python3
"""
Script to manually simulate an Ultravox call to update a candidate's notice period.
This script will:
1. Initiate a call to the specified candidate
2. Simulate the Ultravox API response
3. Trigger the callback to update the candidate's notice period
"""
import asyncio
import argparse
import json
import httpx
import logging
import sys
from datetime import datetime, UTC
from bson import ObjectId

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Default candidate and job IDs
DEFAULT_CANDIDATE_ID = "67bd8328b318f42cb1aa9ed2"
DEFAULT_JOB_ID = "67b5f915f4ab151ec65cce54"
DEFAULT_PHONE = "+919007696846"

async def simulate_notice_period_call(candidate_id=DEFAULT_CANDIDATE_ID, job_id=DEFAULT_JOB_ID, notice_period="2 months", api_base_url="http://localhost:8000"):
    """
    Simulate the entire flow of a voice screening call focused on notice period collection
    """
    try:
        logger.info(f"Simulating notice period call for candidate {candidate_id}")
        
        # Step 1: Initiate a voice screening call
        async with httpx.AsyncClient() as client:
            # Get authentication token
            auth_response = await client.post(
                f"{api_base_url}/api/v1/auth/token",
                data={
                    "username": "admin@example.com",
                    "password": "admin"
                }
            )
            
            if auth_response.status_code != 200:
                logger.error(f"Authentication failed: {auth_response.text}")
                return
            
            auth_data = auth_response.json()
            token = auth_data.get("access_token")
            
            # Initiate voice screening
            logger.info("Initiating voice screening call")
            screening_response = await client.post(
                f"{api_base_url}/api/v1/candidates/{job_id}/screen/{candidate_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if screening_response.status_code != 200:
                logger.error(f"Failed to initiate screening: {screening_response.text}")
                return
            
            screening_data = screening_response.json()
            call_id = screening_data.get("call_id")
            
            logger.info(f"Voice screening initiated with call_id: {call_id}")
            
            # Sleep briefly to simulate call in progress
            await asyncio.sleep(2)
            
            # Step 2: Simulate call completion webhook
            logger.info("Simulating call completion webhook")
            
            # Create mock webhook data
            webhook_data = {
                "CallSid": call_id,
                "CallStatus": "completed",
                "Duration": "30",
                "To": DEFAULT_PHONE,
                "From": "+14155551234"
            }
            
            # Send webhook to simulate call completion
            webhook_response = await client.post(
                f"{api_base_url}/api/v1/candidates/callback/call-complete",
                json=webhook_data
            )
            
            if webhook_response.status_code != 200:
                logger.error(f"Failed to process webhook: {webhook_response.text}")
                return
            
            logger.info("Call completion webhook processed successfully")
            
            # Step 3: Check if the candidate was updated with notice period
            await asyncio.sleep(2)  # Wait for processing to complete
            
            # Get updated candidate data
            candidate_response = await client.get(
                f"{api_base_url}/api/v1/candidates/{job_id}/candidates/{candidate_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if candidate_response.status_code != 200:
                logger.error(f"Failed to get updated candidate: {candidate_response.text}")
                return
            
            candidate_data = candidate_response.json()
            updated_notice_period = candidate_data.get("notice_period")
            screening_score = candidate_data.get("screening_score")
            screening_summary = candidate_data.get("screening_summary")
            screening_in_progress = candidate_data.get("screening_in_progress", True)
            
            logger.info(f"Updated candidate data:")
            logger.info(f"Notice Period: {updated_notice_period}")
            logger.info(f"Screening Score: {screening_score}")
            logger.info(f"Screening Summary: {screening_summary}")
            logger.info(f"Screening In Progress: {screening_in_progress}")
            
            if updated_notice_period == notice_period:
                logger.info("✅ SUCCESS: Notice period was updated correctly!")
            else:
                logger.error(f"❌ FAILURE: Notice period was not updated. Expected: {notice_period}, Actual: {updated_notice_period}")
                
            if not screening_in_progress:
                logger.info("✅ SUCCESS: Screening in progress was correctly set to False!")
            else:
                logger.error("❌ FAILURE: Screening in progress was not updated to False.")
                
    except Exception as e:
        logger.error(f"Error in simulation: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Simulate a voice screening call to update notice period")
    parser.add_argument("--candidate-id", default=DEFAULT_CANDIDATE_ID, help="Candidate ID to test with")
    parser.add_argument("--job-id", default=DEFAULT_JOB_ID, help="Job ID to test with")
    parser.add_argument("--notice-period", default="2 months", help="Notice period value to set")
    parser.add_argument("--api-url", default="http://localhost:8000", help="Base API URL")
    
    args = parser.parse_args()
    
    asyncio.run(simulate_notice_period_call(
        candidate_id=args.candidate_id,
        job_id=args.job_id,
        notice_period=args.notice_period,
        api_base_url=args.api_url
    ))

if __name__ == "__main__":
    main() 