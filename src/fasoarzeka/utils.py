"""
Utility functions for Arzeka Payment API
"""

import base64
import hashlib
import uuid
from typing import Mapping, Optional, Union
from urllib.parse import parse_qs, urlsplit

from .i18n import _

# Name of the query parameter added by the gateway to linkBackToCallingWebsite.
# The official documentation spells it both "paymentRequestId" and "paymentRequestID".
PAYMENT_REQUEST_ID_PARAM = "paymentRequestId"


def get_reference() -> str:
    """
    Generate a unique reference ID (mappedOrderId) for payment transactions

    A random UUID4, as in the official API examples (36 characters, the API
    accepts up to 50). Unique across processes and servers.
    Example: 9b1248cc-dad4-4f1e-baa1-16410de1ecec

    Returns:
        str: Unique reference ID
    """
    return str(uuid.uuid4())


def get_payment_request_id(
    query: Union[str, Mapping[str, object]],
) -> Optional[str]:
    """
    Extract the payment reference from the gateway's return to the merchant site

    After payment, the gateway redirects the user to linkBackToCallingWebsite
    with ``?paymentRequestId=<mappedOrderId>``. The parameter name is matched
    case-insensitively (the documentation uses both spellings).

    Warning:
        This value comes from the user's browser and can be forged. Always
        confirm the payment with check_payment() before delivering anything.

    Args:
        query: Full return URL, raw query string, or a mapping of query
            parameters (e.g. ``request.args`` in Flask, ``request.GET`` in Django)

    Returns:
        The mappedOrderId, or None if the parameter is absent or empty

    Example:
        >>> get_payment_request_id("https://shop.example/retour?paymentRequestID=9b12")
        '9b12'
    """
    if isinstance(query, str):
        if "?" in query or "://" in query:
            query = urlsplit(query).query
        params: Mapping[str, object] = {
            key: values[-1] for key, values in parse_qs(query).items()
        }
    else:
        params = query

    wanted = PAYMENT_REQUEST_ID_PARAM.lower()
    for key, value in params.items():
        if key.lower() == wanted:
            if isinstance(value, (list, tuple)):
                value = value[-1] if value else None
            value = str(value).strip() if value is not None else ""
            return value or None
    return None


def format_msisdn(phone_number: str) -> str:
    """
    Format phone number to Arzeka API format (international without '+')

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


def generate_hash_signature(
    hash_secret: str,
    amount: str,
    merchantId: str,
    mappedOrderId: str,
    linkBackToCallingWebsite: str,
    linkForUpdateStatus: str,
    additionalInfo: str,
    field_order: list = None,
) -> str:
    """
    Generate a SHA256 hash signature for payment data using the provided secret.

    This function creates a secure hash signature by concatenating payment parameters
    in a specific order with the secret key, then generating a SHA256 hash.

    Args:
        secret (str): The secret key used for hashing. Must not be empty.
        amount (str, optional): Payment amount
        merchant_id (str, optional): Merchant identifier
        mapped_order_id (str, optional): Order identifier
        link_back_to_calling_website (str, optional): Callback URL
        link_for_update_status (str, optional): Status update URL
        additional_info (str, optional): Additional information
        field_order (list, optional): Custom order of fields. If None, uses default order.
        **kwargs: Additional parameters (for backward compatibility)

    Returns:
        str: Base64-encoded SHA256 hash signature

    Raises:
        ValueError: If secret is empty or None
        TypeError: If secret is not a string

    Examples:
        >>> secret = "my_secret_key"
        >>> signature = generate_hash_signature(
        ...     secret=secret,
        ...     amount="1000",
        ...     merchant_id="MERCHANT123",
        ...     mapped_order_id="ORDER456"
        ... )
        >>> len(signature)  # Base64 encoded SHA256 is 44 characters
        44

        >>> # Using custom field order
        >>> custom_order = ["amount", "merchant_id", "mapped_order_id"]
        >>> signature = generate_hash_signature(
        ...     secret=secret,
        ...     amount="1000",
        ...     merchant_id="MERCHANT123",
        ...     mapped_order_id="ORDER456",
        ...     field_order=custom_order
        ... )

    Security Note:
        - The secret key should be kept confidential
        - Use HTTPS when transmitting signatures
        - Validate signatures on both client and server sides
    """
    # Input validation
    if not hash_secret:
        raise ValueError(_("Secret key cannot be empty or None"))
    if not isinstance(hash_secret, str):
        raise TypeError(_("Secret key must be a string"))

    # Merge explicit parameters with kwargs for backward compatibility
    params = {
        "amount": amount,
        "merchantId": merchantId,
        "mappedOrderId": mappedOrderId,
        "linkBackToCallingWebsite": linkBackToCallingWebsite,
        "linkForUpdateStatus": linkForUpdateStatus,
        "additionalInfo": additionalInfo,
    }

    # Default field order (Arzeka API standard)
    default_order = [
        "amount",
        "merchantId",
        "mappedOrderId",
        "linkBackToCallingWebsite",
        "linkForUpdateStatus",
        "additionalInfo",
    ]

    # Use custom order if provided, otherwise use default
    order = field_order if field_order is not None else default_order

    # Build message string by concatenating parameters in specified order
    message_parts = []
    for field in order:
        value = params.get(field, "")
        # Convert None to empty string for consistent hashing
        message_parts.append(str(value) if value is not None else "")

    # Add hash_secret at the end
    message_parts.append(hash_secret)

    # Join with pipe separator (Arzeka API standard)
    message = "|".join(message_parts)

    # Generate SHA256 hash
    try:
        hash_digest = hashlib.sha256(message.encode("utf-8")).digest()
        signature = base64.b64encode(hash_digest).decode("utf-8")
        return signature
    except Exception as e:
        raise RuntimeError(
            _("Failed to generate hash signature: %(err)s") % {"err": e}
        )
