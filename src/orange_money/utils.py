"""
Utility functions for OrangeMoney Payment API
"""

from datetime import datetime


def get_reference() -> str:
    """
    Generate a unique reference ID for payment transactions

    Format: {YYMMDD}.{HHMMSS}.{microseconds}
    Example: 251022.143025.123456

    Returns:
        str: Unique reference ID
    """
    reference = datetime.now().strftime("%y%m%d.%H%M%S.%f")
    return f"{reference}"


def format_msisdn(phone_number: str) -> str:
    """
    Format phone number to OrangeMoney API format (international without '+')

    Args:
        phone_number: Phone number in various formats

    Returns:
        str: Formatted phone number

    Examples:
        >>> format_msisdn("+226 70 12 34 56")
        "22670123456"
        >>> format_msisdn("226-70-12-34-56")
        "22670123456"
    """
    # Remove common separators and the '+' sign
    cleaned = (
        phone_number.replace("+", "")
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
    return cleaned


def validate_phone_number(msisdn: str, country_code: str = "226") -> bool:
    """
    Validate phone number format for Burkina Faso

    Args:
        msisdn: Phone number to validate
        country_code: Country code (default: 226 for Burkina Faso)

    Returns:
        bool: True if valid, False otherwise
    """
    cleaned = format_msisdn(msisdn)

    # Check if it starts with the country code
    if not cleaned.startswith(country_code):
        return False

    # Check length (country code + 8 digits for BF)
    expected_length = len(country_code) + 8
    if len(cleaned) != expected_length:
        return False

    # Check if all characters are digits
    return cleaned.isdigit()
