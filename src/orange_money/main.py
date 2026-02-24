"""
Faso OrangeMoney Payment Gateway API Client
Unofficial API client for OrangeMoney mobile money payments in Burkina Faso
"""

from typing import Any, Dict, Optional, Tuple

from .base import OrangeMoneyPayment, logger
from .constants import BASE_URL, DEFAULT_TIMEOUT
from .exceptions import OrangeMoneyAuthenticationError

# Shared client instance for convenience functions
_shared_client: Optional[OrangeMoneyPayment] = None
_shared_client_config: Dict[str, Any] = {}


def _get_shared_client(
    url: str = None,
    timeout: int = DEFAULT_TIMEOUT,
    username: str = None,
    password: str = None,
    phonenumber: str = None,
) -> OrangeMoneyPayment:
    """
    Get or create a shared OrangeMoneyPayment client instance

    Args:
        base_url: Base URL for the API
        timeout: Request timeout in seconds

    Returns:
        Shared OrangeMoneyPayment instance
    """
    global _shared_client, _shared_client_config

    # Check if we need to create a new client or if config changed
    current_config = {"url": url, "timeout": timeout}

    if _shared_client is None or _shared_client_config != current_config:
        # Close existing client if any
        if _shared_client is not None:
            try:
                _shared_client.close()
            except Exception as e:
                logger.debug(f"Error closing previous shared client: {e}")

        # Create new client
        _shared_client = OrangeMoneyPayment(
            base_url=url,
            timeout=timeout,
            username=username,
            password=password,
            phonenumber=phonenumber,
        )
        _shared_client_config = current_config
        logger.debug("Created new shared OrangeMoneyPayment client")

    return _shared_client


def get_shared_client() -> Optional[OrangeMoneyPayment]:
    """
    Get the current shared client instance if it exists

    Returns:
        The shared OrangeMoneyPayment instance or None if not initialized

    Example:
        >>> authenticate("user", "password")
        >>> client = get_shared_client()
        >>> if client and client.is_token_valid():
        ...     print("Shared client has valid token")
    """
    return _shared_client


def close_shared_client() -> None:
    """
    Close and cleanup the shared client instance

    Example:
        >>> authenticate("user", "password")
        >>> # ... do some operations ...
        >>> close_shared_client()  # Cleanup when done
    """
    global _shared_client, _shared_client_config

    if _shared_client is not None:
        try:
            _shared_client.close()
            logger.info("Shared client closed")
        except Exception as e:
            logger.error(f"Error closing shared client: {e}")
        finally:
            _shared_client = None
            _shared_client_config = {}


def make_payment(
    customer_phone: str,
    customer_otp: str,
    amount: int,
    message: str,
    phonenumber: str = None,
    username: str = None,
    password: str = None,
    timeout: int = DEFAULT_TIMEOUT,
    url: str = None,
    reference: str = None,
    verify_ssl: bool = True,
    is_test: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function to make a payment using shared client instance

    Uses the shared OrangeMoneyPayment instance. First authenticates using provided
    credentials if needed, then makes the payment.

    Args:
        customer_phone (str): Customer's phone number
        customer_otp (str): Customer's OTP code
        amount (int): Payment amount in cents
        message (str): Payment description/label
        phonenumber (str, optional): Merchant phone number for authentication
        username (str, optional): API username for authentication
        password (str, optional): API password for authentication
        base_url (str, optional): API base URL
        timeout (int, optional): Request timeout in seconds
        url (str, optional): Custom API URL (overrides is_test)
        reference (str, optional): Transaction reference (auto-generated if None)
        verify_ssl (bool, optional): Whether to verify SSL certificates. Defaults to True.
        is_test (bool, optional): Whether to use test environment. Defaults to True.

    Returns:
        dict: API response with keys:
            - status: Transaction status code
            - message: Status message
            - trans_id: Transaction ID

    Raises:
        OrangeMoneyAuthenticationError: If authentication fails
        OrangeMoneyValidationError: If validation fails
        OrangeMoneyConnectionError: If connection fails

    Example:
        >>> response = make_payment(
        ...     customer_phone="70123456",
        ...     customer_otp="123456",
        ...     amount=1000,
        ...     message="Payment for order #123",
        ...     username="test_user",
        ...     password="test_pass",
        ...     phonenumber="70999999"
        ... )
        >>> if response["status"] == "OM-000":
        ...     print(f"Payment successful: {response['trans_id']}")
    """
    client = _get_shared_client(url, timeout, username, password, phonenumber)

    # Update client credentials if provided
    if phonenumber is not None:
        client._phonenumber = phonenumber
    if username is not None:
        client._username = username
    if password is not None:
        client._password = password

    # Make the payment
    return client.make_payment(
        customer_phone=customer_phone,
        customer_otp=customer_otp,
        amount=amount,
        message=message,
        url=url,
        reference=reference,
        verify_ssl=verify_ssl,
        is_test=is_test,
    )
