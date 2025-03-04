import pytest
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.utils.phone_utils import format_phone_number, is_valid_e164

class TestPhoneUtils:
    """Test suite for phone number utility functions"""
    
    def test_format_phone_number_us(self):
        """Test formatting US phone numbers"""
        # Test various US number formats
        assert format_phone_number("555-123-4567") == "+15551234567"
        assert format_phone_number("(555) 123-4567") == "+15551234567"
        assert format_phone_number("5551234567") == "+15551234567"
        assert format_phone_number("555.123.4567") == "+15551234567"
        assert format_phone_number("555 123 4567") == "+15551234567"
        
        # Test with country code already included
        assert format_phone_number("+15551234567") == "+15551234567"
        assert format_phone_number("15551234567") == "+15551234567"
        
        # Test with extra spaces and characters
        assert format_phone_number(" 555-123-4567 ") == "+15551234567"
        assert format_phone_number("+1 (555) 123-4567") == "+15551234567"
    
    def test_format_phone_number_international(self):
        """Test formatting international phone numbers"""
        # Test UK number
        assert format_phone_number("+447911123456") == "+447911123456"
        assert format_phone_number("447911123456") == "+447911123456"
        
        # Test Indian number
        assert format_phone_number("+919876543210") == "+919876543210"
        assert format_phone_number("919876543210") == "+919876543210"
        
        # Test Australian number
        assert format_phone_number("+61412345678") == "+61412345678"
        
        # Test with spaces and formatting
        assert format_phone_number("+44 7911 123456") == "+447911123456"
        assert format_phone_number("+91 98765 43210") == "+919876543210"
    
    def test_format_phone_number_edge_cases(self):
        """Test edge cases for phone number formatting"""
        # Empty and None values
        assert format_phone_number("") is None
        assert format_phone_number(None) is None
        
        # Invalid formats
        assert format_phone_number("abc123") is None  # Non-numeric should return None
        assert format_phone_number("12") is None  # Too short
    
    def test_is_valid_e164(self):
        """Test E.164 format validation"""
        # Valid numbers
        assert is_valid_e164("+15551234567") is True
        assert is_valid_e164("+447911123456") is True
        assert is_valid_e164("+919876543210") is True
        
        # Invalid numbers
        assert is_valid_e164("") is False
        assert is_valid_e164(None) is False
        assert is_valid_e164("abc123") is False
        assert is_valid_e164("123") is False  # Too short
        assert is_valid_e164("+1234567890123456") is False  # Too long
        assert is_valid_e164("5551234567") is False  # Missing + prefix 