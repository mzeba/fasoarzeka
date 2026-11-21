"""
Arzeka Payment API Client
Unofficial API client for Faso Arzeka mobile money payments in Burkina Faso
"""

import logging
from importlib.metadata import PackageNotFoundError, version

from .base import ArzekaPayment
from .constants import PRODUCTION_BASE_URL, TEST_BASE_URL, PaymentStatus
from .exceptions import (
    ArzekaAPIError,
    ArzekaAuthenticationAPIError,
    ArzekaAuthenticationError,
    ArzekaConnectionError,
    ArzekaPaymentError,
    ArzekaValidationError,
)
from .i18n import install_translations
from .main import (
    authenticate,
    check_payment,
    check_sms_status,
    close_shared_client,
    get_shared_client,
    initiate_payment,
    send_sms,
)
from .utils import (
    format_msisdn,
    generate_hash_signature,
    get_payment_request_id,
    get_reference,
    validate_phone_number,
)

# Libraries must not configure logging: silence "no handler" warnings and
# let the application decide where logs go.
logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    __version__ = version("fasoarzeka")
except PackageNotFoundError:  # running from a source checkout, not installed
    __version__ = "0.0.0+unknown"

__author__ = "Mohamed Zeba (m.zeba@mzeba.dev)"
__all__ = [
    # Classes
    "ArzekaPayment",
    # Constants
    "PaymentStatus",
    "TEST_BASE_URL",
    "PRODUCTION_BASE_URL",
    # Exceptions
    "ArzekaPaymentError",
    "ArzekaAuthenticationError",
    "ArzekaAuthenticationAPIError",
    "ArzekaAPIError",
    "ArzekaValidationError",
    "ArzekaConnectionError",
    # Functions
    "initiate_payment",
    "check_payment",
    "authenticate",
    "close_shared_client",
    "get_shared_client",
    "send_sms",
    "check_sms_status",
    # Utility functions
    "get_reference",
    "get_payment_request_id",
    "format_msisdn",
    "validate_phone_number",
    "generate_hash_signature",
    # i18n
    "install_translations",
]
