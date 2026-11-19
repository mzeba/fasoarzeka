"""Tests de non-régression : comportements sûrs attendus d'une bibliothèque de paiement."""

import os
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

import requests

from fasoarzeka import (
    ArzekaAPIError,
    ArzekaAuthenticationAPIError,
    ArzekaAuthenticationError,
    ArzekaPayment,
    ArzekaValidationError,
)

VALID_INFO = {"firstname": "A", "lastname": "B", "mobile": "70000000"}


class TestRetryPolicy(unittest.TestCase):
    def test_post_is_never_retried(self):
        """Rejouer un POST (initiate_payment) pourrait créer un double paiement."""
        with ArzekaPayment() as client:
            retry = client._session.get_adapter("https://example.com").max_retries
        self.assertNotIn("POST", retry.allowed_methods)
        self.assertIn("GET", retry.allowed_methods)


class TestLogging(unittest.TestCase):
    def test_import_does_not_configure_root_logger(self):
        code = (
            "import logging, fasoarzeka;"
            "print(len(logging.getLogger().handlers), logging.getLogger().level)"
        )
        env = dict(os.environ, PYTHONPATH=os.pathsep.join(sys.path))
        out = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, env=env, check=True
        ).stdout.split()
        self.assertEqual(out[0], "0", "l'import ne doit pas ajouter de handler racine")
        self.assertEqual(out[1], "30", "le niveau racine doit rester WARNING")


class TestValidationBeforeToken(unittest.TestCase):
    """Les paramètres invalides sont rejetés sans ré-authentification ni appel réseau."""

    def setUp(self):
        self.client = ArzekaPayment()
        patcher = patch.object(ArzekaPayment, "_ensure_valid_token")
        self.ensure = patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.client.close)

    def _assert_rejected(self, func, **kwargs):
        with self.assertRaises(ArzekaValidationError):
            func(**kwargs)
        self.ensure.assert_not_called()

    def test_initiate_payment(self):
        self._assert_rejected(
            self.client.initiate_payment,
            amount=10,
            merchant_id="M1",
            link_for_update_status="https://example.com/cb",
            link_back_to_calling_website="https://example.com",
            additional_info=dict(VALID_INFO),
            hash_secret="secret",
        )

    def test_check_payment(self):
        self._assert_rejected(self.client.check_payment, mapped_order_id="")

    def test_send_sms(self):
        self._assert_rejected(self.client.send_sms, mobile="", message="hello")

    def test_check_sms_status(self):
        self._assert_rejected(self.client.check_sms_status, sms_id="")


class TestAuthenticationHttpErrors(unittest.TestCase):
    """Les erreurs HTTP d'authentification restent capturables des deux façons."""

    def _authenticate_with_status(self, status_code):
        response = Mock(status_code=status_code, text="error")
        response.json.return_value = {"error": "x"}
        response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            f"{status_code} Error"
        )
        with ArzekaPayment() as client, patch(
            "fasoarzeka.base.requests.Session.post", return_value=response
        ):
            with self.assertRaises(ArzekaAuthenticationAPIError) as ctx:
                client.authenticate("user", "pwd")
        return ctx.exception

    def test_401_invalid_credentials(self):
        exc = self._authenticate_with_status(401)
        self.assertIsInstance(exc, ArzekaAuthenticationError)
        self.assertIsInstance(exc, ArzekaAPIError)
        self.assertEqual(exc.status_code, 401)
        self.assertIn("Invalid credentials", str(exc))

    def test_403_forbidden(self):
        exc = self._authenticate_with_status(403)
        self.assertEqual(exc.status_code, 403)
        self.assertIn("Access forbidden", str(exc))

    def test_500_server_error(self):
        exc = self._authenticate_with_status(500)
        self.assertIsInstance(exc, ArzekaAuthenticationError)
        self.assertIsInstance(exc, ArzekaAPIError)
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.response_data, {"error": "x"})


if __name__ == "__main__":
    unittest.main()
