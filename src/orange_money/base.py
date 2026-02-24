"""
Module base pour les opérations de paiement OrangeMoney.

Ce module fournit la classe de base `BasePayment` qui gère toutes les interactions
avec l'API OrangeMoney Mobile Money Payment au Burkina Faso. Il inclut :

- Gestion des sessions HTTP avec retry automatique
- Authentification OAuth2 avec gestion des tokens
- Initialisation et vérification des paiements
- Envoi et vérification de SMS
- Gestion complète des erreurs et logging

Classes:
    BasePayment: Classe de base pour toutes les opérations de paiement OrangeMoney.
                 Fournit les méthodes de bas niveau pour interagir avec l'API.

Exceptions:
    OrangeMoneyPaymentError: Exception de base pour toutes les erreurs
    OrangeMoneyConnectionError: Erreurs de connexion réseau
    OrangeMoneyAuthenticationError: Erreurs d'authentification
    OrangeMoneyValidationError: Erreurs de validation des données
    OrangeMoneyAPIError: Erreurs retournées par l'API

Example:
    >>> from fasoarzeka.base import BasePayment
    >>> client = BasePayment()
    >>> auth = client.authenticate("username", "password")
    >>> print(auth['access_token'])

Note:
    Cette classe est destinée à être héritée par des classes plus spécialisées.
    Pour une utilisation standard, utilisez plutôt la classe `OrangeMoneyPayment`.
"""

import logging

from typing import Any, Dict, Optional, Tuple
from urllib.parse import urljoin
import logging
import xml.etree.ElementTree as ET

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .constants import (
    BASE_TEST_URL,
    BASE_PRODUCTION_URL,
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
)
from .exceptions import (
    OrangeMoneyAPIError,
    OrangeMoneyAuthenticationError,
    OrangeMoneyConnectionError,
    OrangeMoneyPaymentError,
    OrangeMoneyValidationError,
)
from .utils import get_reference, validate_phone_number

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BasePayment:
    """
    Base class for OrangeMoney payment operations

    Attributes:

        base_url (str): Base URL for the OrangeMoney API
        timeout (int): Request timeout in seconds
    """

    def __init__(self, base_url: str = None, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the BasePayment client

        Args:
            base_url: Base URL for the API (default: test environment)
            timeout: Request timeout in seconds

        Raises:
            OrangeMoneyValidationError: If token is invalid
        """

        self._token: str = None
        self._token_type: str = None
        self._expires_at: float = None
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self._session = self._create_session()

        logger.info("OrangeMoney payment client initialized")

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic

        Returns:
            Configured requests.Session object
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        # session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(
        self, additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Get request headers with optional additional headers

        Args:
            additional_headers: Optional dictionary of additional headers

        Returns:
            Dictionary of headers
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "fasoarzeka-payment-client/1.0",
            "Accept-Language": "fr-FR,en-GB;q=0.8,en;q=0.6",
            "Authorization": f"{self._token_type} {self._token}",
        }

        if additional_headers:
            headers.update(additional_headers)

        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to OrangeMoney API

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint
            data: Request body data (for POST)
            params: URL parameters (for GET)
            **kwargs: Additional arguments for requests

        Returns:
            Response data as dictionary

        Raises:
            OrangeMoneyConnectionError: If connection fails
            OrangeMoneyAPIError: If API returns an error
        """

        if self._token is None or self._expires_at is None:
            raise OrangeMoneyAuthenticationError(
                "Authentication token is not set. Please authenticate first."
            )

        url = urljoin(self.base_url, endpoint)
        headers = kwargs.pop("headers", {})
        headers = self._get_headers(headers)

        timeout = kwargs.pop("timeout", self.timeout)

        try:
            logger.debug(f"Making {method} request to {url}")

            if method.upper() == "POST":
                response = self._session.post(
                    url, data=data, headers=headers, timeout=timeout, **kwargs
                )
            elif method.upper() == "GET":
                response = self._session.get(
                    url, params=params, headers=headers, timeout=timeout, **kwargs
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check for HTTP errors
            response.raise_for_status()

            # Parse response
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"raw_response": response.text}

            logger.info(f"Request successful: {method} {url}")
            return response_data

        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise OrangeMoneyConnectionError(
                f"Request timeout after {timeout} seconds"
            ) from e

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise OrangeMoneyConnectionError(
                f"Failed to connect to OrangeMoney API: {e}"
            ) from e

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            try:
                error_data = response.json()
            except ValueError:
                error_data = {"error": response.text}

            raise OrangeMoneyAPIError(
                f"API request failed: {e}",
                status_code=response.status_code,
                response_data=error_data,
            ) from e

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise OrangeMoneyPaymentError(f"Unexpected error: {e}") from e

    def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Make POST request to OrangeMoney API

        Args:
            endpoint: API endpoint
            data: Request body data
            **kwargs: Additional arguments

        Returns:
            Response data
        """
        return self._make_request("POST", endpoint, data=data, **kwargs)

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Make GET request to OrangeMoney API

        Args:
            endpoint: API endpoint
            params: URL parameters
            **kwargs: Additional arguments

        Returns:
            Response data
        """
        return self._make_request("GET", endpoint, params=params, **kwargs)

    def close(self):
        """Close the session"""
        if self._session:
            self._session.close()
            logger.info("Session closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


class OrangeMoneyPayment(BasePayment):
    """
    OrangeMoney Payment Gateway client

    Provides methods to initiate and check payment status
    """

    def __init__(
        self,
        base_url: str = None,
        timeout: int = DEFAULT_TIMEOUT,
        phonenumber: str = None,
        username: str = None,
        password: str = None,
    ):
        """
        Initialize OrangeMoney Payment client

        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        super().__init__(base_url, timeout)
        self._phonenumber = phonenumber
        self._username = username
        self._password = password

    def parse_query(
        self,
        customer_phone: str,
        customer_otp: str,
        amount: int,
        libel: str,
        reference=None,
    ):
        """
        Parse payment request data into XML format for Orange Money API.

        Args:
            customer_phone (str): Customer's phone number
            customer_otp (str): Customer's OTP code
            amount (int): Payment amount
            libel (str): Payment description/label
            reference (str, optional): Transaction reference. Auto-generated if None.

        Returns:
            str: XML string formatted for Orange Money API

        Raises:
            ValueError: If any parameter has invalid type or value
        """
        # Validate inputs
        if not isinstance(customer_phone, str) or not customer_phone.strip():
            raise ValueError("Customer phone number must be a non-empty string")
        if not isinstance(customer_otp, str) or not customer_otp.strip():
            raise ValueError("Customer OTP must be a non-empty string")
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError("Amount must be a positive integer")
        if not isinstance(libel, str) or not libel.strip():
            raise ValueError("Label must be a non-empty string")
        if reference is not None and not isinstance(reference, str):
            raise ValueError("Reference must be a string or None")

        logger.info(
            f"Creating payment request for phone: {customer_phone}, amount: {amount}"
        )

        root = ET.Element("COMMAND")

        # Ajouter les éléments enfants à l'élément racine
        ET.SubElement(root, "TYPE").text = "OMPREQ"
        ET.SubElement(root, "customer_msisdn").text = f"{customer_phone}"
        ET.SubElement(root, "merchant_msisdn").text = self._phonenumber
        ET.SubElement(root, "api_username").text = self._username
        ET.SubElement(root, "api_password").text = self._password
        ET.SubElement(root, "amount").text = f"{amount}"
        ET.SubElement(root, "PROVIDER").text = "101"
        ET.SubElement(root, "PROVIDER2").text = "101"
        ET.SubElement(root, "PAYID").text = "12"
        ET.SubElement(root, "PAYID2").text = "12"
        ET.SubElement(root, "otp").text = f"{customer_otp}"
        ET.SubElement(root, "reference_number").text = libel
        ET.SubElement(root, "ext_txn_id").text = reference or get_reference()

        tree = ET.ElementTree(root)
        xml_string = ET.tostring(root, encoding="utf-8").decode("utf-8")

        return xml_string

    def parse_result(self, result: str):
        """
        Parse XML response from Orange Money API.

        Args:
            result (str): Raw XML response from API

        Returns:
            dict: Parsed response with status, message, and transaction ID
        """
        try:
            # Validate input
            if not isinstance(result, str):
                error_msg = f"Result must be a string, got {type(result).__name__}"
                logger.error(error_msg)
                return {
                    "message": error_msg,
                    "status": "OM-500",
                    "trans_id": "Error",
                }

            if not result.strip():
                error_msg = "Empty response received from API"
                logger.error(error_msg)
                return {
                    "message": error_msg,
                    "status": "OM-500",
                    "trans_id": "Error",
                }

            # Parse XML with proper error handling
            try:
                root = ET.fromstring("<root>" + result + "</root>")
            except ET.ParseError as e:
                error_msg = (
                    f"Erreur de parsing XML: {str(e)} - Réponse: {result[:100]}..."
                )
                logger.error(error_msg)
                return {
                    "message": error_msg,
                    "status": "OM-501",
                    "trans_id": "Error",
                }

            # Extract elements with null checks
            status = root.find("status")
            message = root.find("message")
            trans_id = root.find("transID")

            # Check if all required elements are present
            missing_fields = []
            if status is None:
                missing_fields.append("status")
            if message is None:
                missing_fields.append("message")
            if trans_id is None:
                missing_fields.append("transID")

            if missing_fields:
                error_msg = (
                    f"Champs manquants dans la réponse API: {', '.join(missing_fields)}"
                )
                logger.error(f"{error_msg} - Réponse complète: {result}")
                return {
                    "message": error_msg,
                    "status": "OM-500",
                    "trans_id": "Error",
                }

            # Validate that text content exists
            if not status.text or not message.text or not trans_id.text:
                empty_fields = []
                if not status.text:
                    empty_fields.append("status")
                if not message.text:
                    empty_fields.append("message")
                if not trans_id.text:
                    empty_fields.append("transID")

                error_msg = (
                    f"Champs vides dans la réponse API: {', '.join(empty_fields)}"
                )
                logger.error(f"{error_msg} - Réponse complète: {result}")
                return {
                    "message": error_msg,
                    "status": "OM-500",
                    "trans_id": "Error",
                }

            # Successfully parsed response
            response = {
                "status": status.text.strip(),
                "message": message.text.strip(),
                "trans_id": trans_id.text.strip(),
            }
            logger.info(f"Successfully parsed API response: {response}")
            return response

        except Exception as e:
            error_msg = f"Erreur inattendue lors du parsing: {str(e)}"
            logger.exception(error_msg)  # Logs full traceback
            return {
                "message": error_msg,
                "status": "OM-502",
                "trans_id": "Error",
            }

    def make_payment(
        self,
        customer_phone: str,
        customer_otp: str,
        amount: int,
        message: str,
        url: str = None,
        reference=None,
        verify_ssl=True,
        is_test: bool = True,
    ):
        """
        Validate and process payment through Orange Money API.

        Args:
            customer_phone (str): Customer's phone number
            customer_otp (str): Customer's OTP code
            amount (int): Payment amount
            message (str): Payment description
            reference (str, optional): Transaction reference. Auto-generated if None.
            verify_ssl (bool, optional): Whether to verify SSL certificates. Defaults to True.
            is_test (bool, optional): Whether to use the test environment. Defaults to True.
        Returns:
            dict: API response with status, message, and transaction ID

        Raises:
            requests.RequestException: If network request fails
            ValueError: If input validation fails
        """
        try:
            # Determine URL to use: if url is provided, use it; otherwise use is_test
            if not url and (not BASE_TEST_URL or not BASE_PRODUCTION_URL):
                # Only validate default URLs if no custom URL is provided
                error_msg = "API URL not configured"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Prepare request
            headers = {"content-type": "application/xml"}

            try:
                data = self.parse_query(
                    customer_phone, customer_otp, amount, message, reference
                )
            except ValueError as e:
                # Input validation errors from parse_query
                logger.error(f"Validation error: {e}")
                return {
                    "message": f"Erreur de validation des données: {str(e)}",
                    "status": "OM-400",
                    "trans_id": "Error",
                }
            except Exception as e:
                logger.error(f"Error building request: {e}")
                return {
                    "message": f"Erreur de construction de la requête: {str(e)}",
                    "status": "OM-500",
                    "trans_id": "Error",
                }

            # Make HTTP request
            try:
                # Determine which URL to use
                request_url = (
                    url if url else (BASE_TEST_URL if is_test else BASE_PRODUCTION_URL)
                )

                logger.debug(f"Making POST request to {request_url}")

                response = self._session.post(
                    request_url,
                    data=data,
                    headers=headers,
                    timeout=self.timeout,
                    verify=verify_ssl,
                )
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e).lower()

                logger.error(f"{error_type} during request: {e}")

                # Classify error by type
                request_url = (
                    url if url else (BASE_TEST_URL if is_test else BASE_PRODUCTION_URL)
                )

                if "timeout" in error_msg or "timed out" in error_msg:
                    return {
                        "message": f"Timeout de l'API Orange Money ({request_url})",
                        "status": "OM-503",
                        "trans_id": "Error",
                    }
                elif "connection" in error_msg or "resolve" in error_msg:
                    return {
                        "message": f"Erreur de connexion à l'API Orange Money ({request_url})",
                        "status": "OM-504",
                        "trans_id": "Error",
                    }
                elif "ssl" in error_msg or "certificate" in error_msg:
                    return {
                        "message": f"Erreur SSL/Certificat: {str(e)}",
                        "status": "OM-495",
                        "trans_id": "Error",
                    }
                else:
                    return {
                        "message": f"Erreur de requête ({error_type}): {str(e)}",
                        "status": "OM-506",
                        "trans_id": "Error",
                    }

            # Validate HTTP status code
            try:
                response.raise_for_status()
            except Exception as e:
                status_code = (
                    response.status_code
                    if hasattr(response, "status_code")
                    else "Unknown"
                )
                logger.error(f"HTTP {status_code} error: {e}")

                # Try to parse error response anyway
                if hasattr(response, "text") and response.text:
                    result = self.parse_result(response.text)
                    # Add HTTP status info to result
                    if (
                        result.get("status") == "OM-500"
                    ):  # Default error from parse_result
                        result["status"] = f"OM-505-{status_code}"
                        result["message"] = (
                            f"Erreur HTTP {status_code}: {result.get('message', str(e))}"
                        )
                    return result
                else:
                    return {
                        "message": f"Erreur HTTP {status_code}: {str(e)}",
                        "status": "OM-505",
                        "trans_id": "Error",
                    }

            # Parse successful response
            try:
                if not hasattr(response, "text") or not response.text:
                    logger.error("Empty response from API")
                    return {
                        "message": "Réponse vide de l'API Orange Money",
                        "status": "OM-500",
                        "trans_id": "Error",
                    }

                result = self.parse_result(response.text)
                logger.info(f"Payment validation completed: {result.get('status')}")
                return result

            except Exception as e:
                logger.exception(f"Error parsing response: {e}")
                return {
                    "message": f"Erreur de traitement de la réponse: {str(e)}",
                    "status": "OM-502",
                    "trans_id": "Error",
                }

        except ValueError as e:
            # Configuration or validation errors
            logger.error(f"Validation error: {e}")
            return {
                "message": f"Erreur de validation: {str(e)}",
                "status": "OM-400",
                "trans_id": "Error",
            }
        except Exception as e:
            # Catch-all for unexpected errors
            logger.exception(f"Unexpected error in validate_payment: {e}")
            return {
                "message": f"Erreur inattendue ({type(e).__name__}): {str(e)}",
                "status": "OM-506",
                "trans_id": "Error",
            }
