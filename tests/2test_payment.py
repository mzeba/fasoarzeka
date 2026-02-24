import time
import unittest
from unittest.mock import Mock, patch

import requests

from orange_money import (
    OrangeMoneyAuthenticationError,
    OrangeMoneyPayment,
    OrangeMoneyValidationError,
    authenticate,
    check_payment,
    close_shared_client,
    get_shared_client,
    initiate_payment,
)


class TestPaymentVerification(unittest.TestCase):
    """Tests pour la vérification de paiement"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.client = OrangeMoneyPayment()
        # Simule un client authentifié
        self.client._token = "valid_token"
        self.client._expires_at = time.time() + 3600

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.client.close()

    def test_check_payment_validation_empty_order_id(self):
        """Test validation de vérification avec order_id vide"""
        with self.assertRaises(OrangeMoneyValidationError):
            self.client.check_payment(mapped_order_id="")

    def test_check_payment_validation_none_order_id(self):
        """Test validation de vérification avec order_id None"""
        with self.assertRaises(OrangeMoneyValidationError):
            self.client.check_payment(mapped_order_id=None)

    @patch.object(OrangeMoneyPayment, "_ensure_valid_token")
    @patch("fasoarzeka.base.requests.Session.post")
    def test_check_payment_success(self, mock_post, mock_ensure):
        """Test de vérification de paiement réussie"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "completed",
            "mappedOrderId": "ORDER123",
            "amount": 1000,
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client.check_payment(mapped_order_id="ORDER123")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["mappedOrderId"], "ORDER123")
        self.assertEqual(result["amount"], 1000)
        mock_ensure.assert_called_once()
        mock_post.assert_called_once()

    @patch.object(OrangeMoneyPayment, "_ensure_valid_token")
    @patch("fasoarzeka.base.requests.Session.post")
    def test_check_payment_pending(self, mock_post, mock_ensure):
        """Test de vérification de paiement en attente"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "pending",
            "mappedOrderId": "ORDER124",
            "amount": 1500,
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client.check_payment(mapped_order_id="ORDER124")

        self.assertEqual(result["status"], "pending")
        self.assertEqual(result["mappedOrderId"], "ORDER124")

    @patch.object(OrangeMoneyPayment, "_ensure_valid_token")
    @patch("fasoarzeka.base.requests.Session.post")
    def test_check_payment_failed(self, mock_post, mock_ensure):
        """Test de vérification de paiement échoué"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "failed",
            "mappedOrderId": "ORDER125",
            "reason": "Payment rejected",
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client.check_payment(mapped_order_id="ORDER125")

        self.assertEqual(result["status"], "failed")
        self.assertIn("reason", result)

    @patch.object(OrangeMoneyPayment, "_ensure_valid_token")
    @patch("fasoarzeka.base.requests.Session.post")
    def test_check_payment_api_error(self, mock_post, mock_ensure):
        """Test de vérification de paiement avec erreur API"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Order not found"}
        mock_post.return_value = mock_response
        mock_post.return_value.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("404 Not Found")
        )

        with self.assertRaises(Exception):
            self.client.check_payment(mapped_order_id="INVALID_ORDER")


class TestOrangeMoneyPayment(unittest.TestCase):
    """Tests pour la classe OrangeMoneyPayment"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.client = OrangeMoneyPayment()

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.client.close()

    def test_init(self):
        """Test d'initialisation"""
        self.assertIsNone(self.client._token)
        self.assertIsNone(self.client._expires_at)
        self.assertIsNotNone(self.client._session)

    def test_is_token_valid_no_token(self):
        """Test de validité du token quand il n'y a pas de token"""
        self.assertFalse(self.client.is_token_valid())

    def test_is_token_valid_with_valid_token(self):
        """Test de validité du token avec un token valide"""
        self.client._token = "test_token"
        self.client._expires_at = time.time() + 3600  # Expire dans 1 heure
        self.assertTrue(self.client.is_token_valid())

    def test_is_token_valid_with_expired_token(self):
        """Test de validité du token avec un token expiré"""
        self.client._token = "test_token"
        self.client._expires_at = time.time() - 100  # Expiré il y a 100 secondes
        self.assertFalse(self.client.is_token_valid())

    def test_is_token_valid_with_margin(self):
        """Test de validité du token avec marge personnalisée"""
        self.client._token = "test_token"
        self.client._expires_at = time.time() + 30  # Expire dans 30 secondes

        # Avec marge par défaut (60s), devrait être invalide
        self.assertFalse(self.client.is_token_valid())

        # Avec marge de 10s, devrait être valide
        self.assertTrue(self.client.is_token_valid(margin_seconds=10))

    def test_get_token_expiry_info_no_token(self):
        """Test d'info d'expiration sans token"""
        info = self.client.get_token_expiry_info()
        self.assertFalse(info["is_valid"])
        self.assertFalse(info["has_token"])
        self.assertTrue(info["is_expired"])
        self.assertIsNone(info["expires_at"])

    def test_get_token_expiry_info_with_valid_token(self):
        """Test d'info d'expiration avec token valide"""
        self.client._token = "test_token"
        self.client._expires_at = time.time() + 3600

        info = self.client.get_token_expiry_info()
        self.assertTrue(info["is_valid"])
        self.assertTrue(info["has_token"])
        self.assertFalse(info["is_expired"])
        self.assertIsNotNone(info["expires_at"])
        self.assertGreater(info["expires_in_seconds"], 0)
        self.assertGreater(info["expires_in_minutes"], 0)

    @patch("fasoarzeka.base.requests.Session.post")
    def test_authenticate_success(self, mock_post):
        """Test d'authentification réussie"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "token_abc123",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client.authenticate("test_user", "test_password")

        self.assertEqual(result["access_token"], "token_abc123")
        self.assertEqual(result["token_type"], "Bearer")
        self.assertEqual(result["expires_in"], 3600)
        self.assertEqual(self.client._token, "token_abc123")
        self.assertEqual(self.client._username, "test_user")
        self.assertEqual(self.client._password, "test_password")
        self.assertIsNotNone(self.client._expires_at)

    def test_authenticate_validation_errors(self):
        """Test des erreurs de validation d'authentification"""
        # Username vide
        with self.assertRaises(OrangeMoneyValidationError):
            self.client.authenticate("", "password")

        # Password vide
        with self.assertRaises(OrangeMoneyValidationError):
            self.client.authenticate("username", "")

        # Username non-string
        with self.assertRaises(OrangeMoneyValidationError):
            self.client.authenticate(None, "password")

    @patch("fasoarzeka.base.requests.Session.post")
    def test_authenticate_http_401_error(self, mock_post):
        """Test d'erreur 401 lors de l'authentification"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid credentials"}
        mock_post.return_value = mock_response
        mock_post.return_value.raise_for_status.side_effect = (
            requests.exceptions.HTTPError()
        )

        with self.assertRaises(OrangeMoneyAuthenticationError) as context:
            self.client.authenticate("wrong_user", "wrong_password")

        self.assertIn("Invalid credentials", str(context.exception))

    def test_ensure_valid_token_no_credentials(self):
        """Test _ensure_valid_token sans credentials stockés"""
        self.client._token = "expired_token"
        self.client._expires_at = time.time() - 100

        with self.assertRaises(OrangeMoneyAuthenticationError) as context:
            self.client._ensure_valid_token()

        self.assertIn("no credentials stored", str(context.exception))

    @patch.object(OrangeMoneyPayment, "authenticate")
    def test_ensure_valid_token_with_valid_token(self, mock_auth):
        """Test _ensure_valid_token avec token valide"""
        self.client._token = "valid_token"
        self.client._expires_at = time.time() + 3600

        # Ne devrait pas appeler authenticate
        self.client._ensure_valid_token()
        mock_auth.assert_not_called()

    @patch.object(OrangeMoneyPayment, "authenticate")
    def test_ensure_valid_token_auto_reauth(self, mock_auth):
        """Test de réauthentification automatique"""
        self.client._token = "expired_token"
        self.client._expires_at = time.time() - 100
        self.client._username = "test_user"
        self.client._password = "test_pass"

        # Mock authenticate pour qu'il mette à jour le token
        def update_token(username, password):
            self.client._token = "new_token"
            self.client._expires_at = time.time() + 3600
            return {
                "access_token": "new_token",
                "token_type": "Bearer",
                "expires_in": 3600,
            }

        mock_auth.side_effect = update_token

        self.client._ensure_valid_token()
        mock_auth.assert_called_once_with("test_user", "test_pass")

    def test_initiate_payment_validation_amount(self):
        """Test de validation du montant de paiement"""
        payment_data = {
            "merchant_id": "TEST123",
            "additional_info": {
                "first_name": "John",
                "last_name": "Doe",
                "mobile": "70123456",
            },
            "hash_secret": "secret",
            "link_for_update_status": "https://example.com/webhook",
            "link_back_to_calling_website": "https://example.com/return",
        }

        # Montant trop petit
        with self.assertRaises(OrangeMoneyValidationError):
            self.client.initiate_payment(amount=50, **payment_data)

        # Montant négatif
        with self.assertRaises(OrangeMoneyValidationError):
            self.client.initiate_payment(amount=-100, **payment_data)

    def test_initiate_payment_validation_merchant_id(self):
        """Test de validation du merchant_id"""
        payment_data = {
            "amount": 1000,
            "additional_info": {
                "first_name": "John",
                "last_name": "Doe",
                "mobile": "70123456",
            },
            "hash_secret": "secret",
            "link_for_update_status": "https://example.com/webhook",
            "link_back_to_calling_website": "https://example.com/return",
        }

        with self.assertRaises(OrangeMoneyValidationError):
            self.client.initiate_payment(merchant_id="", **payment_data)

    def test_initiate_payment_validation_additional_info(self):
        """Test de validation des additional_info"""
        payment_data = {
            "amount": 1000,
            "merchant_id": "TEST123",
            "hash_secret": "secret",
            "link_for_update_status": "https://example.com/webhook",
            "link_back_to_calling_website": "https://example.com/return",
        }

        # Manque first_name
        with self.assertRaises(OrangeMoneyValidationError):
            self.client.initiate_payment(
                additional_info={"last_name": "Doe", "mobile": "70123456"},
                **payment_data,
            )

    @patch.object(OrangeMoneyPayment, "_ensure_valid_token")
    @patch("fasoarzeka.base.requests.Session.post")
    def test_initiate_payment_success(self, mock_post, mock_ensure):
        """Test de paiement réussi"""
        # Setup
        self.client._token = "valid_token"
        self.client._expires_at = time.time() + 3600

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "mappedOrderId": "ORDER123",
            "paymentUrl": "https://pay.example.com/ORDER123",
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        payment_data = {
            "amount": 1000,
            "merchant_id": "TEST123",
            "additional_info": {
                "first_name": "John",
                "last_name": "Doe",
                "mobile": "70123456",
            },
            "hash_secret": "secret",
            "link_for_update_status": "https://example.com/webhook",
            "link_back_to_calling_website": "https://example.com/return",
        }

        result = self.client.initiate_payment(**payment_data)

        self.assertEqual(result["status"], "success")
        self.assertIn("mappedOrderId", result)
        mock_ensure.assert_called_once()
        mock_post.assert_called_once()

    def test_check_payment_validation(self):
        """Test de validation pour vérification de paiement"""
        with self.assertRaises(OrangeMoneyValidationError):
            self.client.check_payment(mapped_order_id="")

        with self.assertRaises(OrangeMoneyValidationError):
            self.client.check_payment(mapped_order_id=None)

    @patch.object(OrangeMoneyPayment, "_ensure_valid_token")
    @patch("fasoarzeka.base.requests.Session.post")
    def test_check_payment_success(self, mock_post, mock_ensure):
        """Test de vérification de paiement réussie"""
        self.client._token = "valid_token"
        self.client._expires_at = time.time() + 3600

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "completed",
            "mappedOrderId": "ORDER123",
            "amount": 1000,
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client.check_payment(mapped_order_id="ORDER123")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["mappedOrderId"], "ORDER123")
        mock_ensure.assert_called_once()
        mock_post.assert_called_once()


if __name__ == "__main__":
    unittest.main()
