================
Gestion des erreurs
================

Ce guide couvre les stratégies et bonnes pratiques pour gérer les erreurs dans vos applications utilisant Faso Arzeka Payment.

Stratégies de gestion des erreurs
==================================

1. Approche défensive
---------------------

Validez les données avant de les envoyer à l'API.

.. code-block:: python

   from fasoarzeka import ArzekaPayment
   from fasoarzeka.utils import validate_phone_number

   def process_payment(amount, phone, merchant_id):
       # Validation préalable
       if amount < 100:
           raise ValueError("Le montant doit être au moins 100 FCFA")

       if not validate_phone_number(phone):
           raise ValueError("Numéro de téléphone invalide")

       # Procéder au paiement
       with ArzekaPayment() as client:
           client.authenticate("username", "password")
           return client.initiate_payment(
               amount=amount,
               merchant_id=merchant_id,
               additional_info={
                   "first_name": "Client",
                   "last_name": "Test",
                   "mobile": phone
               },
               # ... autres paramètres
           )

2. Retry automatique
--------------------

Implémentez un système de retry pour les erreurs temporaires.

.. code-block:: python

   import time
   from fasoarzeka import (
       ArzekaPayment,
       ArzekaConnectionError,
       ArzekaTimeoutError
   )

   def payment_with_retry(payment_func, max_retries=3):
       """Réessayer une opération avec backoff exponentiel"""
       delay = 1

       for attempt in range(max_retries):
           try:
               return payment_func()
           except (ArzekaConnectionError, ArzekaTimeoutError) as e:
               if attempt == max_retries - 1:
                   raise
               print(f"Tentative {attempt + 1} échouée, réessai dans {delay}s")
               time.sleep(delay)
               delay *= 2  # Backoff exponentiel

       raise Exception("Échec après toutes les tentatives")

   # Utilisation
   def make_payment():
       with ArzekaPayment() as client:
           client.authenticate("username", "password")
           return client.initiate_payment(...)

   response = payment_with_retry(make_payment)

3. Circuit Breaker
------------------

Implémentez un circuit breaker pour éviter de surcharger l'API en cas de problème.

.. code-block:: python

   import time
   from enum import Enum

   class CircuitState(Enum):
       CLOSED = "closed"      # Fonctionnement normal
       OPEN = "open"          # Circuit ouvert, rejette les requêtes
       HALF_OPEN = "half_open"  # Test de récupération

   class CircuitBreaker:
       def __init__(self, failure_threshold=5, timeout=60):
           self.failure_threshold = failure_threshold
           self.timeout = timeout
           self.failure_count = 0
           self.last_failure_time = None
           self.state = CircuitState.CLOSED

       def call(self, func):
           if self.state == CircuitState.OPEN:
               if time.time() - self.last_failure_time > self.timeout:
                   self.state = CircuitState.HALF_OPEN
               else:
                   raise Exception("Circuit breaker is OPEN")

           try:
               result = func()
               self.on_success()
               return result
           except Exception as e:
               self.on_failure()
               raise

       def on_success(self):
           self.failure_count = 0
           self.state = CircuitState.CLOSED

       def on_failure(self):
           self.failure_count += 1
           self.last_failure_time = time.time()

           if self.failure_count >= self.failure_threshold:
               self.state = CircuitState.OPEN

   # Utilisation
   circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=60)

   def make_payment():
       with ArzekaPayment() as client:
           client.authenticate("username", "password")
           return client.initiate_payment(...)

   try:
       response = circuit_breaker.call(make_payment)
   except Exception as e:
       print(f"Payment failed: {e}")

Gestion par type d'erreur
==========================

Erreurs de validation
---------------------

.. code-block:: python

   from fasoarzeka import ArzekaPayment, ArzekaValidationError

   def handle_validation_error():
       client = ArzekaPayment()
       client.authenticate("username", "password")

       try:
           response = client.initiate_payment(
               amount=50,  # Trop petit
               merchant_id="MERCHANT_123",
               # ...
           )
       except ArzekaValidationError as e:
           print(f"Données invalides : {e}")
           # Corriger les données
           response = client.initiate_payment(
               amount=100,  # Corrigé
               merchant_id="MERCHANT_123",
               # ...
           )

Erreurs d'authentification
---------------------------

.. code-block:: python

   from fasoarzeka import ArzekaPayment, ArzekaAuthenticationError

   def handle_auth_error():
       client = ArzekaPayment()

       try:
           client.authenticate("username", "wrong_password")
       except ArzekaAuthenticationError as e:
           print(f"Authentification échouée : {e}")
           # Option 1 : Demander de nouveaux identifiants
           username = input("Username: ")
           password = input("Password: ")
           client.authenticate(username, password)

           # Option 2 : Utiliser des credentials de backup
           client.authenticate(backup_username, backup_password)

Erreurs API
-----------

.. code-block:: python

   from fasoarzeka import check_payment, ArzekaAPIError

   def handle_api_error(order_id):
       try:
           status = check_payment(order_id)
           return status
       except ArzekaAPIError as e:
           if e.status_code == 404:
               print("Commande introuvable")
               return None
           elif e.status_code == 500:
               print("Erreur serveur, réessai...")
               time.sleep(5)
               return check_payment(order_id)  # Réessayer
           else:
               print(f"Erreur API : {e}")
               raise

Erreurs de connexion
---------------------

.. code-block:: python

   from fasoarzeka import authenticate, ArzekaConnectionError
   import time

   def handle_connection_error():
       max_retries = 5
       delay = 2

       for attempt in range(max_retries):
           try:
               auth = authenticate("username", "password")
               return auth
           except ArzekaConnectionError as e:
               if attempt < max_retries - 1:
                   print(f"Connexion échouée, réessai dans {delay}s...")
                   time.sleep(delay)
                   delay *= 2  # Backoff exponentiel
               else:
                   print("Impossible de se connecter")
                   # Envoyer une alerte
                   send_alert("Arzeka API unreachable")
                   raise

Patterns de gestion d'erreurs
==============================

Pattern 1 : Try-Except simple
------------------------------

Pour les opérations simples :

.. code-block:: python

   from fasoarzeka import check_payment, ArzekaPaymentError

   try:
       status = check_payment("ORDER-001")
       print(f"Status: {status['status']}")
   except ArzekaPaymentError as e:
       print(f"Erreur : {e}")

Pattern 2 : Gestion multi-niveaux
----------------------------------

Pour les opérations complexes :

.. code-block:: python

   from fasoarzeka import (
       ArzekaPayment,
       ArzekaValidationError,
       ArzekaAuthenticationError,
       ArzekaAPIError,
       ArzekaConnectionError
   )

   def process_payment_safe(payment_data):
       try:
           with ArzekaPayment() as client:
               # Niveau 1 : Authentification
               try:
                   client.authenticate("username", "password")
               except ArzekaAuthenticationError:
                   # Utiliser credentials de secours
                   client.authenticate(backup_user, backup_pass)

               # Niveau 2 : Validation
               try:
                   response = client.initiate_payment(**payment_data)
               except ArzekaValidationError as e:
                   # Corriger et réessayer
                   payment_data['amount'] = max(payment_data['amount'], 100)
                   response = client.initiate_payment(**payment_data)

               return response

       except ArzekaConnectionError:
           # Mettre en queue pour traitement ultérieur
           queue_payment(payment_data)
           raise
       except ArzekaAPIError as e:
           # Logger et alerter
           logger.error(f"API error: {e}", extra={'status_code': e.status_code})
           send_alert(f"Payment API error: {e}")
           raise

Pattern 3 : Décorateur de retry
--------------------------------

.. code-block:: python

   import functools
   import time
   from fasoarzeka import ArzekaConnectionError, ArzekaTimeoutError

   def retry(max_attempts=3, delay=1, backoff=2):
       """Décorateur pour réessayer une fonction en cas d'erreur"""
       def decorator(func):
           @functools.wraps(func)
           def wrapper(*args, **kwargs):
               current_delay = delay
               for attempt in range(max_attempts):
                   try:
                       return func(*args, **kwargs)
                   except (ArzekaConnectionError, ArzekaTimeoutError) as e:
                       if attempt == max_attempts - 1:
                           raise
                       time.sleep(current_delay)
                       current_delay *= backoff
               return None
           return wrapper
       return decorator

   # Utilisation
   @retry(max_attempts=3, delay=2, backoff=2)
   def check_payment_with_retry(order_id):
       return check_payment(order_id)

   status = check_payment_with_retry("ORDER-001")

Intégration avec frameworks web
================================

Flask
-----

.. code-block:: python

   from flask import Flask, jsonify, request
   from fasoarzeka import (
       ArzekaPayment,
       ArzekaValidationError,
       ArzekaAPIError,
       ArzekaConnectionError
   )

   app = Flask(__name__)
   client = ArzekaPayment()

   @app.errorhandler(ArzekaValidationError)
   def handle_validation_error(e):
       return jsonify({'error': 'Données invalides', 'details': str(e)}), 400

   @app.errorhandler(ArzekaAPIError)
   def handle_api_error(e):
       return jsonify({
           'error': 'Erreur API',
           'status_code': e.status_code,
           'details': str(e)
       }), 502

   @app.errorhandler(ArzekaConnectionError)
   def handle_connection_error(e):
       return jsonify({'error': 'Service temporairement indisponible'}), 503

   @app.route('/api/payment', methods=['POST'])
   def create_payment():
       data = request.json

       try:
           if not client.is_token_valid():
               client.authenticate("username", "password")

           response = client.initiate_payment(
               amount=data['amount'],
               merchant_id=data['merchant_id'],
               # ... autres paramètres
           )

           return jsonify(response), 200

       except ArzekaValidationError:
           raise  # Géré par errorhandler
       except ArzekaAPIError:
           raise  # Géré par errorhandler
       except Exception as e:
           logger.error(f"Unexpected error: {e}")
           return jsonify({'error': 'Erreur interne'}), 500

Django
------

.. code-block:: python

   from django.http import JsonResponse
   from django.views import View
   from fasoarzeka import (
       ArzekaPayment,
       ArzekaValidationError,
       ArzekaAPIError
   )
   import logging

   logger = logging.getLogger(__name__)

   class PaymentView(View):
       def __init__(self):
           super().__init__()
           self.client = ArzekaPayment()

       def post(self, request):
           try:
               if not self.client.is_token_valid():
                   self.client.authenticate("username", "password")

               response = self.client.initiate_payment(
                   amount=request.POST['amount'],
                   merchant_id=request.POST['merchant_id'],
                   # ...
               )

               return JsonResponse(response, status=200)

           except ArzekaValidationError as e:
               return JsonResponse({
                   'error': 'Données invalides',
                   'details': str(e)
               }, status=400)

           except ArzekaAPIError as e:
               logger.error(f"API error: {e}")
               return JsonResponse({
                   'error': 'Erreur de traitement'
               }, status=502)

           except Exception as e:
               logger.exception("Unexpected error")
               return JsonResponse({
                   'error': 'Erreur interne'
               }, status=500)

Monitoring et alerting
======================

Configuration de Sentry
------------------------

.. code-block:: python

   import sentry_sdk
   from sentry_sdk.integrations.logging import LoggingIntegration
   from fasoarzeka import ArzekaPayment, ArzekaPaymentError

   # Configurer Sentry
   sentry_sdk.init(
       dsn="your-sentry-dsn",
       integrations=[LoggingIntegration(level=logging.INFO)]
   )

   def process_payment():
       try:
           with ArzekaPayment() as client:
               client.authenticate("username", "password")
               return client.initiate_payment(...)
       except ArzekaPaymentError as e:
           # Capturer l'erreur dans Sentry
           sentry_sdk.capture_exception(e)
           raise

Métriques personnalisées
-------------------------

.. code-block:: python

   import time
   from prometheus_client import Counter, Histogram

   # Définir les métriques
   payment_requests = Counter(
       'arzeka_payment_requests_total',
       'Total payment requests',
       ['status']
   )
   payment_duration = Histogram(
       'arzeka_payment_duration_seconds',
       'Payment request duration'
   )

   def process_payment_with_metrics():
       start_time = time.time()

       try:
           with ArzekaPayment() as client:
               client.authenticate("username", "password")
               response = client.initiate_payment(...)

           payment_requests.labels(status='success').inc()
           return response

       except ArzekaPaymentError as e:
           payment_requests.labels(status='error').inc()
           raise
       finally:
           duration = time.time() - start_time
           payment_duration.observe(duration)

Checklist de production
========================

Avant de déployer en production, assurez-vous de :

✅ **Gestion des erreurs**

* [ ] Toutes les exceptions sont capturées
* [ ] Les erreurs sont loggées avec détails
* [ ] Messages utilisateur clairs et localisés
* [ ] Retry implémenté pour erreurs temporaires

✅ **Monitoring**

* [ ] Logging configuré avec niveau approprié
* [ ] Erreurs remontées dans système de monitoring (Sentry, etc.)
* [ ] Métriques collectées (succès, échecs, durée)
* [ ] Alertes configurées pour erreurs critiques

✅ **Sécurité**

* [ ] Credentials jamais loggés
* [ ] HTTPS utilisé en production
* [ ] Timeout approprié configuré
* [ ] Variables d'environnement utilisées

✅ **Performance**

* [ ] Connection pooling activé
* [ ] Circuit breaker implémenté
* [ ] Rate limiting respecté
* [ ] Cache utilisé si approprié

Voir aussi
==========

* :doc:`exceptions` : Liste complète des exceptions
* :doc:`best_practices` : Bonnes pratiques
* :doc:`logging` : Configuration du logging
