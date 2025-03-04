import asyncio
from twilio.rest import Client
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Hardcoded Twilio credentials (will only be used for this test)
TWILIO_ACCOUNT_SID = "AC2dd7a301619d0ae449ada741a35ed235"
TWILIO_AUTH_TOKEN = "fb4643331618e56c7be9a32aedbc252b"
TWILIO_PHONE_NUMBER = "+19034005920"
TEST_PHONE_NUMBER = "+919007696846"

async def make_test_call():
    """
    Make a simple test call using Twilio
    """
    logger.info(f"Making a test call to {TEST_PHONE_NUMBER} from {TWILIO_PHONE_NUMBER}")
    
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Create a simple TwiML script
        twiml = """
        <Response>
            <Say>Hello from Recruitment AI. This is a test call to verify your phone number integration. Thank you!</Say>
            <Pause length="1"/>
            <Say>Goodbye!</Say>
        </Response>
        """
        
        # Make the call
        call = client.calls.create(
            to=TEST_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            twiml=twiml
        )
        
        logger.info(f"Call initiated with SID: {call.sid}")
        
        # Wait and check call status
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
            "success": True,
            "call_sid": call.sid,
            "status": call.status
        }
    
    except Exception as e:
        logger.error(f"Error making test call: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = asyncio.run(make_test_call())
    logger.info(f"Test call completed with result: {result}") 