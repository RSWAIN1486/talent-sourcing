import asyncio
import os
import sys
import pytest
from dotenv import load_dotenv
from twilio.rest import Client
import logging
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from the root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path)

@pytest.mark.asyncio
async def test_twilio_call_mock(test_phone_number, mock_twilio_client):
    """
    Test making a call using a mock Twilio client (for unit testing)
    """
    try:
        # Use the mock Twilio client from fixtures
        with patch('twilio.rest.Client', return_value=mock_twilio_client):
            # Set up mock call
            mock_call = mock_twilio_client.calls.create.return_value
            mock_call.sid = "CA12345678901234567890123456789012"
            mock_call.status = "queued"
            
            # Create a TwiML response to say a simple message
            twiml = """
            <Response>
                <Say>Hello from Recruitment AI. This is a test call to verify your phone number integration. Thank you.</Say>
                <Pause length="1"/>
                <Say>Goodbye!</Say>
            </Response>
            """
            
            # Make the call
            logger.info(f"Initiating mock call to {test_phone_number}")
            
            client = Client("dummy_sid", "dummy_token")  # Will be patched
            call = client.calls.create(
                to=test_phone_number,
                from_="+19034005920",
                twiml=twiml
            )
            
            logger.info(f"Call initiated with SID: {call.sid}")
            logger.info(f"Initial call status: {call.status}")
            
            # Simulate status changes
            statuses = ["queued", "ringing", "in-progress", "completed"]
            for status in statuses:
                mock_call.status = status
                call = client.calls(call.sid).fetch()
                logger.info(f"Call status updated to: {call.status}")
                
                if status == "completed":
                    logger.info(f"Call completed successfully")
                    break
                
                # Wait a short time in test
                await asyncio.sleep(0.1)
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "to": test_phone_number,
                "from": "+19034005920"
            }
            
    except Exception as e:
        logger.error(f"Error making mock Twilio call: {str(e)}", exc_info=True)
        return {"error": str(e)}

@pytest.mark.asyncio
async def test_twilio_call_real():
    """
    This function tests making a real call using Twilio to a registered phone number.
    Only run this test if you have proper Twilio credentials.
    """
    # Get Twilio credentials from environment variables
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    # Directly set the test phone number
    to_number = "+919007696846"  # Using the phone number provided by the user
    
    # Verify all required variables are present
    missing_vars = []
    if not account_sid:
        missing_vars.append("TWILIO_ACCOUNT_SID")
    if not auth_token:
        missing_vars.append("TWILIO_AUTH_TOKEN")
    if not from_number:
        missing_vars.append("TWILIO_PHONE_NUMBER")
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        pytest.skip(error_msg)
    
    logger.info(f"Using phone number: {to_number}")
    
    # Initialize Twilio client
    try:
        client = Client(account_sid, auth_token)
        logger.info("Successfully initialized Twilio client")
        
        # Create a TwiML response to say a simple message
        twiml = """
        <Response>
            <Say>Hello from Recruitment AI. This is a test call to verify your phone number integration. Thank you.</Say>
            <Pause length="1"/>
            <Say>Goodbye!</Say>
        </Response>
        """
        
        # Make the call
        logger.info(f"Initiating call from {from_number} to {to_number}")
        
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            twiml=twiml
        )
        
        logger.info(f"Call initiated with SID: {call.sid}")
        logger.info(f"Call status: {call.status}")
        
        # Wait for call to be completed or failed
        max_checks = 30  # 30 checks, 2 seconds apart = 1 minute maximum wait
        for i in range(max_checks):
            call = client.calls(call.sid).fetch()
            logger.info(f"Current call status: {call.status}")
            
            if call.status in ["completed", "failed", "busy", "no-answer", "canceled"]:
                logger.info(f"Call ended with status: {call.status}")
                break
                
            # Wait for 2 seconds before checking again
            await asyncio.sleep(2)
        
        return {
            "call_sid": call.sid,
            "status": call.status,
            "to": to_number,
            "from": from_number
        }
        
    except Exception as e:
        logger.error(f"Error making Twilio call: {str(e)}", exc_info=True)
        return {"error": str(e)}

if __name__ == "__main__":
    try:
        # Run the mock test by default to avoid making real calls
        print("\nRunning mock Twilio call test...")
        mock_result = asyncio.run(test_twilio_call_mock("+919007696846", MagicMock()))
        logger.info(f"Mock test completed: {mock_result}")
        
        # Only run the real test if explicitly requested
        if os.getenv("RUN_REAL_CALL_TEST") == "1":
            print("\nRunning real Twilio call test...")
            real_result = asyncio.run(test_twilio_call_real())
            logger.info(f"Real test completed: {real_result}")
            
            # Exit with error code if there was an error
            if "error" in real_result:
                sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1) 