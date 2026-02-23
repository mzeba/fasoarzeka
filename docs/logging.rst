=======
Logging
=======

La bibliothèque Faso Arzeka Payment intègre un système de logging complet pour tracer toutes les opérations.

Configuration de base
=====================

Configuration simple
--------------------

.. code-block:: python

   import logging
   from fasoarzeka import ArzekaPayment

   # Configurer le logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

   # Utiliser le client
   client = ArzekaPayment()
   client.authenticate("username", "password")

Configuration avancée
---------------------

.. code-block:: python

   import logging
   import logging.handlers

   # Créer le logger
   logger = logging.getLogger('fasoarzeka')
   logger.setLevel(logging.DEBUG)

   # Handler pour fichier avec rotation
   file_handler = logging.handlers.RotatingFileHandler(
       'arzeka.log',
       maxBytes=10485760,  # 10MB
       backupCount=5
   )
   file_handler.setLevel(logging.DEBUG)

   # Handler pour console
   console_handler = logging.StreamHandler()
   console_handler.setLevel(logging.INFO)

   # Format
   formatter = logging.Formatter(
       '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   file_handler.setFormatter(formatter)
   console_handler.setFormatter(formatter)

   # Ajouter les handlers
   logger.addHandler(file_handler)
   logger.addHandler(console_handler)

Niveaux de log
==============

DEBUG
-----

Affiche toutes les informations détaillées (requêtes, réponses, etc.).

.. code-block:: python

   logging.basicConfig(level=logging.DEBUG)

   # Affichera :
   # - Requêtes HTTP complètes
   # - Réponses HTTP complètes
   # - Détails de validation
   # - État du token

**Utilisation :** Développement et debugging uniquement

INFO
----

Affiche les événements importants.

.. code-block:: python

   logging.basicConfig(level=logging.INFO)

   # Affichera :
   # - Authentification réussie
   # - Paiement initié
   # - Statut vérifié

**Utilisation :** Production (recommandé)

WARNING
-------

Affiche les avertissements.

.. code-block:: python

   logging.basicConfig(level=logging.WARNING)

   # Affichera :
   # - Token bientôt expiré
   # - Retry en cours
   # - Problèmes non critiques

**Utilisation :** Production minimale

ERROR
-----

Affiche uniquement les erreurs.

.. code-block:: python

   logging.basicConfig(level=logging.ERROR)

   # Affichera :
   # - Échec d'authentification
   # - Erreur API
   # - Erreur de connexion

**Utilisation :** Production strict

Exemples de logs
================

Logs d'authentification
-----------------------

.. code-block:: python

   import logging
   logging.basicConfig(level=logging.INFO)

   client = ArzekaPayment()
   client.authenticate("username", "password")

**Sortie :**

.. code-block:: text

   2026-02-23 10:30:15 - fasoarzeka.base - INFO - Authenticating...
   2026-02-23 10:30:16 - fasoarzeka.base - INFO - Authentication successful
   2026-02-23 10:30:16 - fasoarzeka.base - INFO - Token expires at 2026-02-23 11:30:16

Logs de paiement
----------------

.. code-block:: python

   response = client.initiate_payment(
       amount=1000,
       merchant_id="MERCHANT_123",
       # ...
   )

**Sortie :**

.. code-block:: text

   2026-02-23 10:31:00 - fasoarzeka.base - INFO - Initiating payment...
   2026-02-23 10:31:01 - fasoarzeka.base - INFO - Payment initiated: ORDER-2026-001

Logs de vérification
--------------------

.. code-block:: python

   status = client.check_payment("ORDER-2026-001")

**Sortie :**

.. code-block:: text

   2026-02-23 10:32:00 - fasoarzeka.base - INFO - Checking payment status: ORDER-2026-001
   2026-02-23 10:32:01 - fasoarzeka.base - INFO - Payment status: COMPLETED

Filtrage des logs
=================

Par module
----------

.. code-block:: python

   # Logger uniquement fasoarzeka
   logger = logging.getLogger('fasoarzeka')
   logger.setLevel(logging.DEBUG)

   # Désactiver les logs requests
   logging.getLogger('urllib3').setLevel(logging.WARNING)

Par niveau
----------

.. code-block:: python

   import logging

   class LevelFilter(logging.Filter):
       def __init__(self, level):
           self.level = level

       def filter(self, record):
           return record.levelno == self.level

   # Handler pour erreurs uniquement
   error_handler = logging.FileHandler('errors.log')
   error_handler.addFilter(LevelFilter(logging.ERROR))

Intégration avec applications
==============================

Application Flask
-----------------

.. code-block:: python

   from flask import Flask
   import logging
   from logging.handlers import RotatingFileHandler

   app = Flask(__name__)

   # Configurer le logging Flask
   if not app.debug:
       file_handler = RotatingFileHandler(
           'logs/app.log',
           maxBytes=10240000,
           backupCount=10
       )
       file_handler.setFormatter(logging.Formatter(
           '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
       ))
       file_handler.setLevel(logging.INFO)
       app.logger.addHandler(file_handler)

       # Logger Arzeka
       arzeka_logger = logging.getLogger('fasoarzeka')
       arzeka_logger.addHandler(file_handler)

Application Django
------------------

.. code-block:: python

   # settings.py
   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           'verbose': {
               'format': '{levelname} {asctime} {module} {message}',
               'style': '{',
           },
       },
       'handlers': {
           'file': {
               'level': 'INFO',
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': 'logs/django.log',
               'maxBytes': 10485760,
               'backupCount': 5,
               'formatter': 'verbose',
           },
       },
       'loggers': {
           'fasoarzeka': {
               'handlers': ['file'],
               'level': 'INFO',
               'propagate': False,
           },
       },
   }

Logging structuré
=================

JSON Logging
------------

.. code-block:: python

   import json
   import logging

   class JsonFormatter(logging.Formatter):
       def format(self, record):
           log_data = {
               'timestamp': self.formatTime(record),
               'level': record.levelname,
               'logger': record.name,
               'message': record.getMessage(),
           }
           if record.exc_info:
               log_data['exception'] = self.formatException(record.exc_info)
           return json.dumps(log_data)

   handler = logging.StreamHandler()
   handler.setFormatter(JsonFormatter())

   logger = logging.getLogger('fasoarzeka')
   logger.addHandler(handler)

**Sortie :**

.. code-block:: json

   {"timestamp": "2026-02-23 10:30:15", "level": "INFO", "logger": "fasoarzeka.base", "message": "Authentication successful"}

Avec contexte personnalisé
---------------------------

.. code-block:: python

   import logging

   logger = logging.getLogger('fasoarzeka')

   # Ajouter du contexte
   logger.info("Payment initiated", extra={
       'order_id': 'ORDER-001',
       'amount': 1000,
       'customer_id': 'CUST-123'
   })

Monitoring et alerting
======================

Intégration Sentry
------------------

.. code-block:: python

   import sentry_sdk
   from sentry_sdk.integrations.logging import LoggingIntegration

   # Configurer Sentry
   sentry_logging = LoggingIntegration(
       level=logging.INFO,
       event_level=logging.ERROR
   )

   sentry_sdk.init(
       dsn="your-sentry-dsn",
       integrations=[sentry_logging]
   )

   # Les erreurs seront automatiquement envoyées à Sentry
   logger = logging.getLogger('fasoarzeka')
   logger.error("Payment failed", exc_info=True)

CloudWatch Logs
---------------

.. code-block:: python

   import boto3
   from watchtower import CloudWatchLogHandler

   # Créer le handler CloudWatch
   cloudwatch_handler = CloudWatchLogHandler(
       log_group='arzeka-payments',
       stream_name='production'
   )

   logger = logging.getLogger('fasoarzeka')
   logger.addHandler(cloudwatch_handler)

Bonnes pratiques
================

1. **Ne jamais logger les secrets**

   .. code-block:: python

      # ❌ MAUVAIS
      logger.info(f"Password: {password}")
      logger.debug(f"Hash secret: {hash_secret}")

      # ✅ BON
      logger.info("Authenticating...")
      logger.debug("Hash secret: ***")

2. **Utiliser les niveaux appropriés**

   .. code-block:: python

      # ✅ BON
      logger.debug("Detailed trace information")
      logger.info("Important business event")
      logger.warning("Something unexpected happened")
      logger.error("Operation failed", exc_info=True)

3. **Inclure le contexte**

   .. code-block:: python

      # ✅ BON
      logger.info(f"Payment initiated for order {order_id}")
      logger.error(f"Payment failed for order {order_id}", exc_info=True)

4. **Rotation des logs**

   .. code-block:: python

      from logging.handlers import RotatingFileHandler

      handler = RotatingFileHandler(
          'arzeka.log',
          maxBytes=10485760,  # 10MB
          backupCount=5
      )

5. **Logger les métriques**

   .. code-block:: python

      import time

      start_time = time.time()
      response = client.initiate_payment(...)
      duration = time.time() - start_time

      logger.info(f"Payment completed in {duration:.2f}s")

Voir aussi
==========

* :doc:`error_handling` : Gestion des erreurs
* :doc:`best_practices` : Bonnes pratiques
* :doc:`api_reference` : Référence API
