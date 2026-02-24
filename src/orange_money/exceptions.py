from typing import Dict, Optional


class OrangeMoneyPaymentError(Exception):
    """Base exception for OrangeMoney payment errors"""

    pass


class OrangeMoneyConnectionError(OrangeMoneyPaymentError):
    """Exception raised when connection to OrangeMoney API fails"""

    pass


class OrangeMoneyValidationError(OrangeMoneyPaymentError):
    """Exception raised when payment data validation fails"""

    pass


class OrangeMoneyAPIError(OrangeMoneyPaymentError):
    """Exception raised when OrangeMoney API returns an error"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class OrangeMoneyAuthenticationError(OrangeMoneyPaymentError):
    """Exception raised when authentication fails"""

    pass
