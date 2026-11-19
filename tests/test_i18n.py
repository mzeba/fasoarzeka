import builtins
import gettext
import os
import unittest

from fasoarzeka import (
    ArzekaAuthenticationError,
    ArzekaPayment,
    ArzekaValidationError,
    check_payment,
    close_shared_client,
    i18n,
    install_translations,
)
from fasoarzeka.utils import generate_hash_signature

MO_FR = os.path.join(i18n.LOCALE_DIR, "fr", "LC_MESSAGES", f"{i18n.DOMAIN}.mo")


class TestI18n(unittest.TestCase):
    """Tests de la traduction des messages d'erreur"""

    def setUp(self):
        self.client = ArzekaPayment()

    def tearDown(self):
        self.client.close()
        close_shared_client()
        # Revenir aux messages anglais par défaut
        i18n._translation = gettext.NullTranslations()

    def _message(self, exc_type, func, *args, **kwargs):
        with self.assertRaises(exc_type) as ctx:
            func(*args, **kwargs)
        return str(ctx.exception)

    def test_default_messages_are_english(self):
        msg = self._message(ArzekaValidationError, self.client.authenticate, "", "pwd")
        self.assertEqual(msg, "username must be a non-empty string")

    def test_install_french_translates_messages(self):
        install_translations("fr")
        msg = self._message(ArzekaValidationError, self.client.authenticate, "", "pwd")
        self.assertEqual(msg, "Le nom d'utilisateur doit être une chaîne non vide")

    def test_regional_code_falls_back_to_language(self):
        install_translations("fr_FR")
        msg = self._message(ArzekaValidationError, self.client.authenticate, "user", "")
        self.assertEqual(msg, "Le mot de passe doit être une chaîne non vide")

    def test_placeholders_are_formatted(self):
        install_translations("fr")
        self.client._token = "token"
        self.client._expires_at = 9999999999
        msg = self._message(
            ArzekaValidationError,
            self.client.initiate_payment,
            amount=10,
            merchant_id="M1",
            link_for_update_status="https://example.com/cb",
            link_back_to_calling_website="https://example.com",
            additional_info={"firstname": "A", "lastname": "B", "mobile": "70000000"},
            hash_secret="secret",
        )
        self.assertIn("100", msg)
        self.assertNotIn("%(", msg)
        self.assertTrue(msg.startswith("Le montant"), msg)

    def test_unknown_language_keeps_english(self):
        translation = install_translations("xx")
        self.assertNotIsInstance(translation, gettext.GNUTranslations)
        msg = self._message(ArzekaValidationError, self.client.authenticate, "", "pwd")
        self.assertEqual(msg, "username must be a non-empty string")

    def test_utils_messages_are_translated(self):
        install_translations("fr")
        msg = self._message(
            ValueError, generate_hash_signature, "", "1000", "M1", "O1", "a", "b", "{}"
        )
        self.assertEqual(msg, "La clé secrète ne peut pas être vide ou None")

    def test_does_not_touch_builtins(self):
        had_underscore = hasattr(builtins, "_")
        install_translations("fr")
        self.assertEqual(hasattr(builtins, "_"), had_underscore)

    def test_shared_client_message_translated(self):
        install_translations("fr")
        msg = self._message(ArzekaAuthenticationError, check_payment, "order-1")
        self.assertTrue(msg.startswith("Non authentifié"), msg)


class TestCatalogs(unittest.TestCase):
    """Le catalogue français doit être compilé et complet"""

    def test_french_catalog_is_compiled(self):
        self.assertTrue(os.path.isfile(MO_FR), f"{MO_FR} manquant")

    def test_french_catalog_is_complete(self):
        with open(MO_FR, "rb") as fp:
            catalog = gettext.GNUTranslations(fp)._catalog
        untranslated = [k for k, v in catalog.items() if k and not v]
        self.assertEqual(untranslated, [])
        # 29 messages traduits + l'en-tête
        self.assertGreaterEqual(len(catalog), 30)


if __name__ == "__main__":
    unittest.main()
