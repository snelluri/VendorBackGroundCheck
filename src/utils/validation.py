"""
Input validation and sanitization utilities for the Vendor Background Check application.
"""
import re
from typing import Any, Optional, Tuple, Union
from urllib.parse import urlparse

import html

class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass

def sanitize_string(input_str: str, max_length: int = 255) -> str:
    """
    Sanitize a string input by removing potentially dangerous characters.
    
    Args:
        input_str: The input string to sanitize
        max_length: Maximum allowed length of the string
        
    Returns:
        Sanitized string
        
    Raises:
        ValidationError: If the input is not a string or exceeds max_length
    """
    if not isinstance(input_str, str):
        raise ValidationError("Input must be a string")
    
    if len(input_str) > max_length:
        raise ValidationError(f"Input exceeds maximum length of {max_length} characters")
    
    # Remove any HTML/script tags and escape special characters
    sanitized = html.escape(input_str.strip())
    
    # Remove any remaining HTML entities that might have been created by escape
    sanitized = re.sub(r'&[^;]+;', '', sanitized)
    
    return sanitized

def validate_url(url: str) -> str:
    """
    Validate and sanitize a URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        Sanitized URL
        
    Raises:
        ValidationError: If the URL is invalid
    """
    try:
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValidationError("Invalid URL format")
        
        # Only allow http and https schemes
        if parsed.scheme not in ('http', 'https'):
            raise ValidationError("Only http and https URLs are allowed")
        
        return url
    except Exception as e:
        raise ValidationError(f"Invalid URL: {str(e)}")

def validate_email(email: str) -> str:
    """
    Validate and sanitize an email address.
    
    Args:
        email: The email address to validate
        
    Returns:
        Sanitized email address
        
    Raises:
        ValidationError: If the email is invalid
    """
    email = email.strip()
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValidationError("Invalid email format")
    
    return email

def validate_phone_number(phone: str) -> str:
    """
    Validate and sanitize a phone number.
    
    Args:
        phone: The phone number to validate
        
    Returns:
        Sanitized phone number (digits only)
        
    Raises:
        ValidationError: If the phone number is invalid
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Basic validation for US phone numbers (10 digits)
    if len(digits) not in (10, 11):
        raise ValidationError("Phone number must be 10 digits (or 11 with country code)")
    
    return digits

def validate_business_name(name: str) -> str:
    """
    Validate and sanitize a business name.
    
    Args:
        name: The business name to validate
        
    Returns:
        Sanitized business name
        
    Raises:
        ValidationError: If the business name is invalid
    """
    name = sanitize_string(name, 100)
    
    # Basic validation - allow letters, numbers, spaces, and common punctuation
    if not re.match(r'^[\w\s\-\'&,.()]+$', name):
        raise ValidationError("Business name contains invalid characters")
    
    return name.strip()

def validate_search_query(query: str) -> str:
    """
    Validate and sanitize a search query.
    
    Args:
        query: The search query to validate
        
    Returns:
        Sanitized search query
        
    Raises:
        ValidationError: If the search query is invalid
    """
    query = sanitize_string(query, 500)
    
    # Remove any potentially dangerous characters
    query = re.sub(r'[<>{}[\]\\]', '', query)
    
    return query.strip()
