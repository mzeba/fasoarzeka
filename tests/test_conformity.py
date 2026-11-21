"""
Conformité avec la documentation officielle de la passerelle FASO ARZEKA (v2.0).

Les valeurs d'exemple (mappedOrderId, liens, additionalInfo...) reprennent celles
de la documentation officielle.
"""

import base64
import hashlib
import json
import time
import unittest
import uuid
from decimal import Decimal
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

import requests

from fasoarzeka import (
    PRODUCTION_BASE_URL,
    TEST_BASE_URL,
    ArzekaAPIError,
    ArzekaPayment,
    ArzekaValidationError,
    PaymentStatus,
    get_payment_request_id,
    get_reference,
)

DOC_ORDER_ID = "9b1248cc-dad4-4f1e-baa1-16410de1ecec"
DOC_INFO = {"firstname": "Test", "lastname": "Test", "mobile": "22612345678"}


def ok_response(payload):
    response = Mock(status_code=200)
    response.json.return_value = payload
    response.raise_for_status = Mock()
    return response


def http_error(status_code):
    response = Mock(status_code=status_code, text="error")
    response.json.return_value = {"error": "x"}
    response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        f"{status_code} Error"
    )
    return response


class AuthenticatedClientTestCase(unittest.TestCase):
    def setUp(self):
        self.client = ArzekaPayment()
        self.client._token = "TOKEN"
        self.client._token_type = "Bearer"
        self.client._expires_at = time.time() + 3600
        self.addCleanup(self.client.close)

    def initiate(self, **overrides):
        kwargs = dict(
            amount=1000,
            merchant_id="1",
            mapped_order_id=DOC_ORDER_ID,
            link_back_to_calling_website="about:blank",
            link_for_update_status="http://localhost",
            additional_info=dict(DOC_INFO),
            hash_secret="SECRET",
        )
        kwargs.update(overrides)
        return self.client.initiate_payment(**kwargs)


class TestBaseUrls(unittest.TestCase):
    def test_official_urls(self):
        self.assertEqual(TEST_BASE_URL, "https://pgw-test.fasoarzeka.bf/")
        self.assertEqual(PRODUCTION_BASE_URL, "https://pgw.fasoarzeka.bf/")

    def test_default_is_test_environment(self):
        with ArzekaPayment() as client:
            self.assertEqual(client.base_url, TEST_BASE_URL)


class TestInitializePayment(AuthenticatedClientTestCase):
    def test_request_matches_documentation(self):
        with patch(
            "requests.Session.post", return_value=ok_response({"url": "https://pay"})
        ) as post:
            response, sent = self.initiate()

        url = post.call_args.args[0]
        data = post.call_args.kwargs["data"]
        headers = post.call_args.kwargs["headers"]

        self.assertEqual(
            url,
            TEST_BASE_URL + "AvepayPaymentGatewayUI/avepay-payment/app/initializePayment",
        )
        self.assertEqual(headers["Authorization"], "Bearer TOKEN")
        self.assertEqual(headers["Content-Type"], "application/x-www-form-urlencoded")
        self.assertEqual(
            set(data),
            {
                "amount",
                "merchantId",
                "mappedOrderId",
                "linkBackToCallingWebsite",
                "linkForUpdateStatus",
                "additionalInfo",
                "hashString",
            },
        )
        self.assertEqual(data["linkBackToCallingWebsite"], "YWJvdXQ6Ymxhbms=")
        self.assertEqual(data["linkForUpdateStatus"], "aHR0cDovL2xvY2FsaG9zdA==")
        self.assertEqual(response, {"url": "https://pay"})
        self.assertIs(sent, data)

    def test_hash_follows_official_algorithm(self):
        with patch("requests.Session.post", return_value=ok_response({"url": "x"})):
            _, sent = self.initiate()
        expected_data = "|".join(
            [
                str(sent["amount"]),
                sent["merchantId"],
                sent["mappedOrderId"],
                sent["linkBackToCallingWebsite"],
                sent["linkForUpdateStatus"],
                sent["additionalInfo"],
                "SECRET",
            ]
        )
        expected = base64.b64encode(
            hashlib.sha256(expected_data.encode("utf-8")).digest()
        ).decode()
        self.assertEqual(sent["hashString"], expected)

    def test_additional_info_is_compact_json_with_required_fields(self):
        with patch("requests.Session.post", return_value=ok_response({"url": "x"})):
            _, sent = self.initiate()
        self.assertNotIn(" ", sent["additionalInfo"])
        info = json.loads(sent["additionalInfo"])
        self.assertEqual({k: info[k] for k in DOC_INFO}, DOC_INFO)

    def test_caller_additional_info_is_not_modified(self):
        info = dict(DOC_INFO)
        with patch("requests.Session.post", return_value=ok_response({"url": "x"})):
            self.initiate(additional_info=info)
        self.assertEqual(info, DOC_INFO)

    def test_receipt_fields_required_when_generate_receipt(self):
        info = dict(DOC_INFO, generateReceipt=True)
        with self.assertRaises(ArzekaValidationError):
            self.initiate(additional_info=info)

    def test_amount_types(self):
        with patch("requests.Session.post", return_value=ok_response({"url": "x"})):
            _, sent = self.initiate(amount=Decimal("1500"))
            self.assertEqual(str(sent["amount"]), "1500")
            self.initiate(amount=100)  # minimum inclus
        for invalid in (99, 0, -5, True, "1000", float("nan"), float("inf"), Decimal("NaN")):
            with self.subTest(amount=invalid), self.assertRaises(ArzekaValidationError):
                self.initiate(amount=invalid)

    def test_additional_info_must_be_a_dict(self):
        with self.assertRaises(ArzekaValidationError):
            self.initiate(additional_info='{"firstname": "Test"}')


class TestCheckPayment(AuthenticatedClientTestCase):
    def _query_sent(self, *args, **kwargs):
        with patch(
            "requests.Session.post", return_value=ok_response({"status": "PENDING"})
        ) as post:
            self.client.check_payment(*args, **kwargs)
        url = post.call_args.args[0]
        self.assertIsNone(post.call_args.kwargs.get("data"))
        return urlsplit(url), parse_qs(urlsplit(url).query)

    def test_request_matches_documentation(self):
        parts, query = self._query_sent(DOC_ORDER_ID, transaction_id="T1")
        self.assertTrue(
            parts.path.endswith(
                "/AvepayPaymentGatewayUI/avepay-payment/app/getThirdPartyMapInfo"
            )
        )
        self.assertEqual(query, {"mappedOrderId": [DOC_ORDER_ID], "transId": ["T1"]})

    def test_special_characters_are_url_encoded(self):
        _, query = self._query_sent("A&B C+D#1", transaction_id="x/y?z")
        self.assertEqual(query, {"mappedOrderId": ["A&B C+D#1"], "transId": ["x/y?z"]})

    def test_not_found_is_api_error_404(self):
        with patch("requests.Session.post", return_value=http_error(404)):
            with self.assertRaises(ArzekaAPIError) as ctx:
                self.client.check_payment(DOC_ORDER_ID)
        self.assertEqual(ctx.exception.status_code, 404)


class TestReauthenticationOn403(AuthenticatedClientTestCase):
    def test_reauthenticates_once_then_retries(self):
        self.client._username, self.client._password = "user", "pwd"
        responses = [http_error(403), ok_response({"status": "COMPLETED"})]
        with patch("requests.Session.post", side_effect=responses), patch.object(
            ArzekaPayment, "authenticate"
        ) as auth:
            result = self.client.check_payment(DOC_ORDER_ID)
        auth.assert_called_once_with("user", "pwd")
        self.assertEqual(result["status"], "COMPLETED")

    def test_second_403_is_raised(self):
        self.client._username, self.client._password = "user", "pwd"
        with patch(
            "requests.Session.post", side_effect=[http_error(403), http_error(403)]
        ), patch.object(ArzekaPayment, "authenticate") as auth:
            with self.assertRaises(ArzekaAPIError) as ctx:
                self.client.check_payment(DOC_ORDER_ID)
        auth.assert_called_once()
        self.assertEqual(ctx.exception.status_code, 403)

    def test_without_credentials_403_is_raised(self):
        with patch("requests.Session.post", return_value=http_error(403)), patch.object(
            ArzekaPayment, "authenticate"
        ) as auth:
            with self.assertRaises(ArzekaAPIError):
                self.client.check_payment(DOC_ORDER_ID)
        auth.assert_not_called()

    def test_other_errors_do_not_reauthenticate(self):
        self.client._username, self.client._password = "user", "pwd"
        with patch("requests.Session.post", return_value=http_error(404)), patch.object(
            ArzekaPayment, "authenticate"
        ) as auth:
            with self.assertRaises(ArzekaAPIError):
                self.client.check_payment(DOC_ORDER_ID)
        auth.assert_not_called()


class TestReferencesAndStatuses(unittest.TestCase):
    def test_get_reference_is_uuid4(self):
        ref = get_reference()
        self.assertEqual(uuid.UUID(ref).version, 4)
        self.assertLessEqual(len(ref), 50)  # String(50)
        self.assertEqual(len({get_reference() for _ in range(1000)}), 1000)

    def test_payment_statuses(self):
        self.assertEqual(set(PaymentStatus.ALL), {"COMPLETED", "INCOMPLETE", "PENDING"})


class TestPaymentRequestId(unittest.TestCase):
    def test_extraction(self):
        cases = {
            "https://shop.example/retour?paymentRequestId=abc": "abc",
            "https://shop.example/retour?paymentRequestID=abc&x=1": "abc",
            "paymentRequestID=" + DOC_ORDER_ID: DOC_ORDER_ID,
            "?paymentrequestid=a%26b": "a&b",
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                self.assertEqual(get_payment_request_id(query), expected)

    def test_mappings(self):
        self.assertEqual(get_payment_request_id({"paymentRequestID": "abc"}), "abc")
        self.assertEqual(get_payment_request_id({"paymentRequestId": ["a", "b"]}), "b")

    def test_missing_or_empty(self):
        self.assertIsNone(get_payment_request_id("https://shop.example/retour"))
        self.assertIsNone(get_payment_request_id({"paymentRequestId": "  "}))
        self.assertIsNone(get_payment_request_id({}))


if __name__ == "__main__":
    unittest.main()
