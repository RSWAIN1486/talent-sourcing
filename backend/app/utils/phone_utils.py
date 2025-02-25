import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def format_phone_number(phone_number: str) -> Optional[str]:
    """
    Format a phone number into E.164 format for Twilio
    
    Args:
        phone_number: Phone number in any format
        
    Returns:
        Formatted phone number in E.164 format or None if invalid
    """
    if not phone_number:
        return None
    
    # Remove any non-digit characters except the + sign at the beginning
    digits_only = re.sub(r'[^\d+]', '', phone_number)
    
    # If the number doesn't start with a +, determine what to add
    if not digits_only.startswith('+'):
        # If it starts with a country code like 1 (US), 91 (India), etc.
        if len(digits_only) >= 10:
            # If it's a 10-digit number, assume it's a US number and add +1
            if len(digits_only) == 10:
                digits_only = '+1' + digits_only
            # If it starts with a recognized country code, add + sign
            elif digits_only.startswith('1') or digits_only.startswith('91'):
                digits_only = '+' + digits_only
            else:
                # Default to adding + sign if it's long enough to be a full number
                digits_only = '+' + digits_only
        else:
            # Not enough digits for a valid international number
            logger.warning(f"Phone number too short: {phone_number}")
            return None
    
    # Validate that the number seems reasonable
    # E.164 format: + followed by country code and subscriber number, no spaces
    # Typical length is 10-15 digits
    if not re.match(r'^\+\d{10,15}$', digits_only):
        logger.warning(f"Invalid phone number format after processing: {digits_only}")
        return None
    
    return digits_only

def is_valid_e164(phone_number: str) -> bool:
    """
    Check if a phone number is in valid E.164 format
    
    Args:
        phone_number: Phone number to check
        
    Returns:
        True if the phone number is in valid E.164 format, False otherwise
    """
    if not phone_number:
        return False
    
    # E.164 format: + followed by country code and subscriber number, no spaces
    return bool(re.match(r'^\+\d{10,15}$', phone_number)) 