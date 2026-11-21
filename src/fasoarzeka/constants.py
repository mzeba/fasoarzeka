# Constants

# Base URLs of the FASO ARZEKA payment gateway (official documentation v2.0)
TEST_BASE_URL = "https://pgw-test.fasoarzeka.bf/"
PRODUCTION_BASE_URL = "https://pgw.fasoarzeka.bf/"
BASE_URL = TEST_BASE_URL  # default used by the client (kept for compatibility)

PAYMENT_BASE_URL = "AvepayPaymentGatewayUI/avepay-payment/"
INITIATE_PAYMENT_ENDPOINT = "app/initializePayment"
AUTH_ENDPOINT = "auth/getToken"
PAYMENT_VERIFICATION_ENDPOINT = "app/getThirdPartyMapInfo"

SMS_BASE_URL = "ArzekaSmsSender/"
SEND_SMS = "sendSms"
CHECK_SMS_STATUS = "checkSms"


class PaymentStatus:
    """
    Payment statuses returned by check_payment() in the ``status`` field.

    Lifecycle observed on the gateway: INIT (created, payment page never
    opened) -> INCOMPLETE (page opened, not paid) -> PENDING -> COMPLETED.
    INIT is not listed in the official documentation (v2.0) but is returned
    by the gateway.
    """

    INIT = "INIT"  # payment created, payment page not opened yet
    INCOMPLETE = "INCOMPLETE"  # payment not completed (page opened, abandoned, failed...)
    PENDING = "PENDING"  # payment in progress
    COMPLETED = "COMPLETED"  # payment succeeded

    ALL = (INIT, INCOMPLETE, PENDING, COMPLETED)


DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
# Library-side safeguard, not an API rule: amounts below this value are rejected
MINIMUM_AMOUNT = 100  # Franc CFA (XOF)
EXPIRATION_MARGIN_SECONDS = 2 * 60  # Default margin for token validity checks
