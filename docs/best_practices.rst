================
Bonnes pratiques
================

Ce guide présente les meilleures pratiques pour utiliser la bibliothèque Faso Arzeka Payment
de manière sûre, performante et maintenable.

Sécurité
========

1. Protéger les credentials
----------------------------

❌ **Ne jamais hard-coder les credentials**

.. code-block:: python

   # ❌ MAUVAIS
   client = ArzekaPayment()
   client.authenticate("username", "password")

✅ **Utiliser des variables d'environnement**

.. code-block:: python

   # ✅ BON
   import os

   client = ArzekaPayment()
   client.authenticate(
       os.getenv('ARZEKA_USERNAME'),
       os.getenv('ARZEKA_PASSWORD')
   )

2. Ne jamais logger les secrets
--------------------------------

.. code-block:: python

   # ❌ MAUVAIS
   logger.info(f"Authenticating with password: {password}")

   # ✅ BON
   logger.info("Authenticating...")

   # ❌ MAUVAIS
   logger.debug(f"Hash secret: {hash_secret}")

   # ✅ BON
   logger.debug("Hash secret: ***")

3. Utiliser HTTPS en production
--------------------------------

.. code-block:: python

   # ✅ BON - Production
   client = ArzekaPayment(
       base_url="https://pwg.fasoarzeka.com/",
       verify_ssl=True
   )

   # ⚠️ Acceptable seulement en test
   client = ArzekaPayment(
       base_url="https://pwg-test.fasoarzeka.com/",
       verify_ssl=False  # Uniquement en test !
   )

4. Valider les webhooks
-----------------------

.. code-block:: python

   @app.route('/webhook', methods=['POST'])
   def webhook():
       data = request.json
       order_id = data.get('mappedOrderId')

       # ✅ Toujours vérifier auprès d'Arzeka
       verified_status = check_payment(order_id)

       if verified_status['status'] == 'COMPLETED':
           # Traiter le paiement
           process_order(order_id)

       return jsonify({'status': 'received'}), 200

Performance
===========

1. Réutiliser les instances client
-----------------------------------

❌ **Créer un nouveau client à chaque requête**

.. code-block:: python

   # ❌ MAUVAIS - Crée une nouvelle session à chaque fois
   def make_payment():
       client = ArzekaPayment()
       client.authenticate("username", "password")
       response = client.initiate_payment(...)
       client.close()
       return response

✅ **Réutiliser le même client**

.. code-block:: python

   # ✅ BON - Réutilise la même session
   client = ArzekaPayment()
   client.authenticate("username", "password")

   def make_payment():
       return client.initiate_payment(...)

   # Faire plusieurs paiements
   payment1 = make_payment()
   payment2 = make_payment()

   # Fermer à la fin
   client.close()

2. Utiliser le Context Manager
-------------------------------

.. code-block:: python

   # ✅ OPTIMAL
   with ArzekaPayment() as client:
       client.authenticate("username", "password")

       # Faire plusieurs opérations
       for order in orders:
           response = client.initiate_payment(...)

3. Configurer un timeout approprié
-----------------------------------

.. code-block:: python

   # ⚠️ Trop court - risque de timeout
   client = ArzekaPayment(timeout=5)

   # ✅ BON - Équilibré
   client = ArzekaPayment(timeout=30)

   # ⚠️ Trop long - bloque l'application
   client = ArzekaPayment(timeout=300)

4. Activer le retry automatique
--------------------------------

.. code-block:: python

   # ✅ BON
   client = ArzekaPayment(
       max_retries=3,
       retry_delay=2
   )

Fiabilité
=========

1. Toujours gérer les erreurs
------------------------------

.. code-block:: python

   from fasoarzeka import (
       ArzekaPayment,
       ArzekaValidationError,
       ArzekaAPIError,
       ArzekaConnectionError
   )

   # ✅ BON
   try:
       response = client.initiate_payment(...)
   except ArzekaValidationError as e:
       logger.error(f"Validation error: {e}")
       return None
   except ArzekaAPIError as e:
       logger.error(f"API error: {e}")
       return None
   except ArzekaConnectionError as e:
       logger.error(f"Connection error: {e}")
       # Réessayer plus tard
       queue_for_retry(payment_data)
       return None

2. Utiliser la réauthentification automatique
----------------------------------------------

.. code-block:: python

   # ✅ BON - Pas besoin de gérer l'expiration du token
   client = ArzekaPayment()
   client.authenticate("username", "password")

   # Le client se réauthentifie automatiquement si nécessaire
   response = client.initiate_payment(...)

3. Valider les données avant envoi
-----------------------------------

.. code-block:: python

   from fasoarzeka.utils import validate_phone_number, format_msisdn

   def process_payment(amount, phone, ...):
       # ✅ Validation en amont
       if amount < 100:
           raise ValueError("Montant minimum : 100 FCFA")

       if not validate_phone_number(phone):
           raise ValueError("Numéro de téléphone invalide")

       # Formatage
       phone = format_msisdn(phone)

       # Envoyer à l'API
       response = client.initiate_payment(
           amount=amount,
           additional_info={
               "mobile": phone,
               # ...
           },
           # ...
       )

4. Implémenter l'idempotence
-----------------------------

.. code-block:: python

   # ✅ BON - Vérifier si déjà traité
   @app.route('/webhook', methods=['POST'])
   def webhook():
       data = request.json
       order_id = data.get('mappedOrderId')

       # Vérifier si déjà traité
       if is_already_processed(order_id):
           logger.info(f"Order {order_id} already processed")
           return jsonify({'status': 'already_processed'}), 200

       # Traiter le paiement
       process_payment(order_id)
       mark_as_processed(order_id)

       return jsonify({'status': 'success'}), 200

Structure du code
=================

1. Organiser les configurations
--------------------------------

.. code-block:: python

   # config.py
   import os
   from dataclasses import dataclass

   @dataclass
   class ArzekaConfig:
       username: str = os.getenv('ARZEKA_USERNAME', '')
       password: str = os.getenv('ARZEKA_PASSWORD', '')
       merchant_id: str = os.getenv('ARZEKA_MERCHANT_ID', '')
       hash_secret: str = os.getenv('ARZEKA_HASH_SECRET', '')
       base_url: str = os.getenv('ARZEKA_BASE_URL', 'https://pwg-test.fasoarzeka.com/')
       webhook_url: str = os.getenv('ARZEKA_WEBHOOK_URL', '')
       return_url: str = os.getenv('ARZEKA_RETURN_URL', '')

   # Utilisation
   from config import ArzekaConfig

   config = ArzekaConfig()
   client = ArzekaPayment(base_url=config.base_url)
   client.authenticate(config.username, config.password)

2. Créer des wrappers métier
-----------------------------

.. code-block:: python

   # payment_service.py
   from fasoarzeka import ArzekaPayment
   from config import ArzekaConfig
   import logging

   logger = logging.getLogger(__name__)

   class PaymentService:
       def __init__(self):
           self.config = ArzekaConfig()
           self.client = ArzekaPayment(base_url=self.config.base_url)
           self.client.authenticate(
               self.config.username,
               self.config.password
           )

       def create_payment(self, amount: int, customer_phone: str, order_id: str):
           """Créer un paiement avec validation et logging"""
           try:
               logger.info(f"Creating payment for order {order_id}")

               response = self.client.initiate_payment(
                   amount=amount,
                   merchant_id=self.config.merchant_id,
                   additional_info={
                       "mobile": customer_phone,
                       # ...
                   },
                   mapped_order_id=order_id,
                   hash_secret=self.config.hash_secret,
                   link_for_update_status=self.config.webhook_url,
                   link_back_to_calling_website=self.config.return_url
               )

               logger.info(f"Payment created: {response['mappedOrderId']}")
               return response

           except Exception as e:
               logger.error(f"Payment creation failed: {e}")
               raise

       def get_payment_status(self, order_id: str):
           """Récupérer le statut d'un paiement"""
           try:
               return self.client.check_payment(order_id)
           except Exception as e:
               logger.error(f"Status check failed for {order_id}: {e}")
               raise

       def close(self):
           """Fermer le client"""
           self.client.close()

3. Séparer les responsabilités
-------------------------------

.. code-block:: python

   # validators.py
   def validate_payment_data(data):
       """Valider les données de paiement"""
       if data['amount'] < 100:
           raise ValueError("Montant minimum : 100 FCFA")
       # ...

   # formatters.py
   def format_payment_response(response):
       """Formater la réponse pour l'API publique"""
       return {
           'order_id': response['mappedOrderId'],
           'payment_url': response['url'],
           'status': response['status']
       }

   # services.py
   def process_payment(payment_data):
       """Traiter un paiement"""
       validate_payment_data(payment_data)

       response = payment_service.create_payment(
           amount=payment_data['amount'],
           customer_phone=payment_data['phone'],
           order_id=payment_data['order_id']
       )

       return format_payment_response(response)

Logging
=======

1. Configurer le logging correctement
--------------------------------------

.. code-block:: python

   import logging

   # Configuration de base
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('arzeka.log'),
           logging.StreamHandler()
       ]
   )

2. Logger les événements importants
------------------------------------

.. code-block:: python

   logger = logging.getLogger(__name__)

   # ✅ BON
   logger.info(f"Payment initiated for order {order_id}")
   logger.info(f"Payment completed: {order_id}")
   logger.warning(f"Token will expire in 5 minutes")
   logger.error(f"Payment failed: {order_id}", exc_info=True)

3. Éviter le logging excessif
------------------------------

.. code-block:: python

   # ❌ MAUVAIS - Trop verbeux
   logger.debug("Entering function")
   logger.debug("Validating data")
   logger.debug("Data validated")
   logger.debug("Calling API")
   logger.debug("API called")

   # ✅ BON - Pertinent
   logger.info(f"Processing payment for order {order_id}")
   logger.info(f"Payment successful: {order_id}")

Tests
=====

1. Tester avec mocks
--------------------

.. code-block:: python

   import unittest
   from unittest.mock import patch, MagicMock
   from fasoarzeka import ArzekaPayment

   class TestPaymentService(unittest.TestCase):
       @patch('fasoarzeka.ArzekaPayment')
       def test_create_payment(self, mock_client):
           # Configurer le mock
           mock_client.return_value.initiate_payment.return_value = {
               'mappedOrderId': 'ORDER-001',
               'url': 'https://...',
               'status': 'PENDING'
           }

           # Tester
           service = PaymentService()
           response = service.create_payment(1000, "22670123456", "ORDER-001")

           # Vérifier
           self.assertEqual(response['mappedOrderId'], 'ORDER-001')

2. Utiliser l'environnement de test
------------------------------------

.. code-block:: python

   # tests/conftest.py
   import os

   os.environ['ARZEKA_BASE_URL'] = 'https://pwg-test.fasoarzeka.com/'
   os.environ['ARZEKA_USERNAME'] = 'test_user'
   os.environ['ARZEKA_PASSWORD'] = 'test_pass'

Production
==========

Checklist de déploiement
-------------------------

✅ **Configuration**

* [ ] Variables d'environnement configurées
* [ ] URL de production utilisée
* [ ] Credentials de production configurés
* [ ] SSL activé

✅ **Logging**

* [ ] Niveau de log approprié (INFO ou WARNING)
* [ ] Rotation des logs configurée
* [ ] Logs centralisés (Sentry, CloudWatch, etc.)

✅ **Monitoring**

* [ ] Métriques collectées
* [ ] Alertes configurées
* [ ] Dashboard créé

✅ **Sécurité**

* [ ] Secrets jamais loggés
* [ ] HTTPS utilisé
* [ ] Webhooks validés
* [ ] Rate limiting implémenté

✅ **Performance**

* [ ] Connection pooling activé
* [ ] Timeout configuré
* [ ] Retry activé
* [ ] Cache implémenté si applicable

✅ **Tests**

* [ ] Tests unitaires passent
* [ ] Tests d'intégration passent
* [ ] Tests en environnement de pré-production

Voir aussi
==========

* :doc:`error_handling` : Gestion des erreurs
* :doc:`logging` : Configuration du logging
* :doc:`api_reference` : Référence API complète
