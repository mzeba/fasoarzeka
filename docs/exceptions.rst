==========
Exceptions
==========

La bibliothèque fournit une hiérarchie d'exceptions personnalisées pour gérer différents types d'erreurs.

Hiérarchie des exceptions
==========================

.. code-block:: text

   ArzekaPaymentError (Exception de base)
   ├── ArzekaValidationError
   ├── ArzekaAuthenticationError
   ├── ArzekaAPIError
   ├── ArzekaConnectionError
   └── ArzekaTimeoutError

Toutes les exceptions héritent de ``ArzekaPaymentError``, ce qui permet de les capturer toutes en une fois si nécessaire.

ArzekaPaymentError
==================

Exception de base pour toutes les erreurs de la bibliothèque.

.. code-block:: python

   class ArzekaPaymentError(Exception):
       """Exception de base pour toutes les erreurs Arzeka"""

**Utilisation:**

.. code-block:: python

   from fasoarzeka import ArzekaPaymentError

   try:
       # ... opérations Arzeka
       pass
   except ArzekaPaymentError as e:
       print(f"Erreur Arzeka : {e}")

ArzekaValidationError
=====================

Levée lorsque les données fournies sont invalides.

**Causes courantes:**

* Montant invalide (< 100 ou non numérique)
* Numéro de téléphone invalide
* Paramètres manquants ou incorrects
* Format de données incorrect

**Exemple:**

.. code-block:: python

   from fasoarzeka import ArzekaPayment, ArzekaValidationError

   client = ArzekaPayment()
   client.authenticate("username", "password")

   try:
       # Montant trop petit
       response = client.initiate_payment(
           amount=50,  # < 100 FCFA
           merchant_id="MERCHANT_123",
           # ... autres paramètres
       )
   except ArzekaValidationError as e:
       print(f"Données invalides : {e}")

ArzekaAuthenticationError
=========================

Levée lors d'un échec d'authentification.

**Causes courantes:**

* Identifiants incorrects (username/password)
* Token expiré
* Token invalide
* Compte verrouillé ou désactivé

**Exemple:**

.. code-block:: python

   from fasoarzeka import ArzekaPayment, ArzekaAuthenticationError

   client = ArzekaPayment()

   try:
       client.authenticate("wrong_user", "wrong_password")
   except ArzekaAuthenticationError as e:
       print(f"Authentification échouée : {e}")
       # Demander à l'utilisateur de réessayer

**Avec réauthentification automatique:**

.. code-block:: python

   try:
       response = client.initiate_payment(...)
   except ArzekaAuthenticationError as e:
       # Token expiré et pas de credentials stockés
       print(f"Réauthentification requise : {e}")
       client.authenticate("username", "password")
       response = client.initiate_payment(...)

ArzekaAPIError
==============

Levée lorsque l'API Arzeka retourne une erreur.

**Attributs:**

* ``status_code`` (int) : Code de statut HTTP (400, 404, 500, etc.)
* ``response_data`` (dict) : Données de réponse de l'API
* ``message`` (str) : Message d'erreur

**Causes courantes:**

* Erreur serveur (500, 502, 503)
* Ressource introuvable (404)
* Requête invalide (400)
* Limite de taux dépassée (429)
* Problème de paiement (solde insuffisant, etc.)

**Exemple:**

.. code-block:: python

   from fasoarzeka import check_payment, ArzekaAPIError

   try:
       status = check_payment("INVALID_ORDER_ID")
   except ArzekaAPIError as e:
       print(f"Erreur API : {e}")
       print(f"Code HTTP : {e.status_code}")
       print(f"Détails : {e.response_data}")

       if e.status_code == 404:
           print("Commande introuvable")
       elif e.status_code == 500:
           print("Erreur serveur, réessayer plus tard")

**Gestion par code de statut:**

.. code-block:: python

   try:
       response = client.initiate_payment(...)
   except ArzekaAPIError as e:
       if e.status_code == 400:
           print("Requête invalide")
       elif e.status_code == 401:
           print("Non autorisé")
       elif e.status_code == 404:
           print("Ressource introuvable")
       elif e.status_code >= 500:
           print("Erreur serveur")
       else:
           print(f"Erreur API : {e}")

ArzekaConnectionError
=====================

Levée lors d'un problème de connexion réseau.

**Causes courantes:**

* Pas de connexion Internet
* Serveur inaccessible
* DNS ne résout pas
* Firewall bloquant la connexion

**Exemple:**

.. code-block:: python

   from fasoarzeka import authenticate, ArzekaConnectionError
   import time

   max_retries = 3

   for attempt in range(max_retries):
       try:
           auth = authenticate("username", "password")
           print("✅ Connexion réussie")
           break
       except ArzekaConnectionError as e:
           print(f"❌ Erreur de connexion (tentative {attempt+1}/{max_retries})")
           if attempt < max_retries - 1:
               time.sleep(2 ** attempt)  # Backoff exponentiel
           else:
               print("Impossible de se connecter après plusieurs tentatives")
               raise

ArzekaTimeoutError
==================

Levée lorsqu'une requête dépasse le timeout configuré.

**Causes courantes:**

* Serveur lent ou surchargé
* Problème réseau intermittent
* Timeout configuré trop court

**Exemple:**

.. code-block:: python

   from fasoarzeka import ArzekaPayment, ArzekaTimeoutError

   client = ArzekaPayment(timeout=5)  # 5 secondes

   try:
       response = client.initiate_payment(...)
   except ArzekaTimeoutError as e:
       print(f"Timeout : {e}")
       # Réessayer avec un timeout plus long
       client.timeout = 30
       response = client.initiate_payment(...)

Gestion globale des erreurs
============================

Approche simple
---------------

Capturer toutes les exceptions Arzeka :

.. code-block:: python

   from fasoarzeka import ArzekaPayment, ArzekaPaymentError

   client = ArzekaPayment()

   try:
       client.authenticate("username", "password")
       response = client.initiate_payment(...)
   except ArzekaPaymentError as e:
       print(f"Erreur : {e}")
       # Logger l'erreur
       logger.error(f"Arzeka error: {e}")

Approche détaillée
------------------

Gérer chaque type d'erreur différemment :

.. code-block:: python

   from fasoarzeka import (
       ArzekaPayment,
       ArzekaValidationError,
       ArzekaAuthenticationError,
       ArzekaAPIError,
       ArzekaConnectionError,
       ArzekaTimeoutError
   )

   client = ArzekaPayment()

   try:
       client.authenticate("username", "password")
       response = client.initiate_payment(
           amount=1000,
           merchant_id="MERCHANT_123",
           # ... autres paramètres
       )

   except ArzekaValidationError as e:
       print(f"❌ Données invalides : {e}")
       # Corriger les données et réessayer

   except ArzekaAuthenticationError as e:
       print(f"❌ Authentification échouée : {e}")
       # Demander de nouveaux identifiants

   except ArzekaAPIError as e:
       print(f"❌ Erreur API (code {e.status_code}) : {e}")
       # Logger et alerter

   except ArzekaConnectionError as e:
       print(f"❌ Erreur de connexion : {e}")
       # Réessayer plus tard

   except ArzekaTimeoutError as e:
       print(f"❌ Timeout : {e}")
       # Réessayer avec timeout plus long

Fonction de retry
-----------------

Créer une fonction de retry personnalisée :

.. code-block:: python

   import time
   from fasoarzeka import (
       ArzekaPayment,
       ArzekaConnectionError,
       ArzekaTimeoutError,
       ArzekaAPIError
   )

   def retry_operation(func, max_retries=3, delay=2):
       """Réessayer une opération en cas d'erreur temporaire"""
       for attempt in range(max_retries):
           try:
               return func()
           except (ArzekaConnectionError, ArzekaTimeoutError) as e:
               if attempt < max_retries - 1:
                   print(f"⚠️ Tentative {attempt+1} échouée, réessai dans {delay}s...")
                   time.sleep(delay)
                   delay *= 2  # Backoff exponentiel
               else:
                   print(f"❌ Échec après {max_retries} tentatives")
                   raise
           except ArzekaAPIError as e:
               # Ne pas réessayer sur erreur API 4xx (erreur client)
               if 400 <= e.status_code < 500:
                   raise
               # Réessayer sur erreur 5xx (erreur serveur)
               if attempt < max_retries - 1:
                   print(f"⚠️ Erreur serveur, réessai dans {delay}s...")
                   time.sleep(delay)
               else:
                   raise

   # Utilisation
   client = ArzekaPayment()
   client.authenticate("username", "password")

   def do_payment():
       return client.initiate_payment(...)

   response = retry_operation(do_payment)

Logging des erreurs
===================

Configuration de base
---------------------

.. code-block:: python

   import logging
   from fasoarzeka import ArzekaPayment, ArzekaPaymentError

   # Configurer le logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   logger = logging.getLogger(__name__)

   client = ArzekaPayment()

   try:
       client.authenticate("username", "password")
       response = client.initiate_payment(...)
   except ArzekaPaymentError as e:
       logger.error(f"Arzeka error: {e}", exc_info=True)

Logging détaillé par type d'erreur
-----------------------------------

.. code-block:: python

   from fasoarzeka import (
       ArzekaValidationError,
       ArzekaAuthenticationError,
       ArzekaAPIError,
       ArzekaConnectionError
   )

   try:
       response = client.initiate_payment(...)
   except ArzekaValidationError as e:
       logger.warning(f"Validation error: {e}")
   except ArzekaAuthenticationError as e:
       logger.error(f"Authentication failed: {e}")
   except ArzekaAPIError as e:
       logger.error(
           f"API error: {e}",
           extra={
               'status_code': e.status_code,
               'response_data': e.response_data
           }
       )
   except ArzekaConnectionError as e:
       logger.critical(f"Connection error: {e}")

Meilleures pratiques
====================

1. **Toujours capturer les exceptions spécifiques**

   .. code-block:: python

      # ✅ BON
      try:
           response = client.initiate_payment(...)
       except ArzekaValidationError:
           # Gérer erreur de validation
       except ArzekaAPIError:
           # Gérer erreur API

      # ❌ MAUVAIS
      try:
           response = client.initiate_payment(...)
       except Exception:
           # Trop général

2. **Logger toutes les erreurs**

   .. code-block:: python

      import logging

      try:
           response = client.initiate_payment(...)
       except ArzekaPaymentError as e:
           logger.error(f"Payment failed: {e}", exc_info=True)
           raise

3. **Fournir des messages utilisateur clairs**

   .. code-block:: python

      try:
           response = client.initiate_payment(...)
       except ArzekaValidationError:
           return "Vérifiez vos informations de paiement"
       except ArzekaConnectionError:
           return "Problème de connexion, réessayez plus tard"
       except ArzekaAPIError as e:
           if e.status_code == 404:
               return "Paiement introuvable"
           return "Erreur lors du traitement du paiement"

4. **Implémenter un système de retry**

   Pour les erreurs temporaires (connexion, timeout, erreur serveur),
   implémentez un système de retry avec backoff exponentiel.

5. **Monitorer les erreurs**

   Utilisez un système de monitoring (Sentry, Datadog, etc.) pour
   suivre les erreurs en production.

Voir aussi
==========

* :doc:`error_handling` : Guide de gestion des erreurs
* :doc:`best_practices` : Bonnes pratiques
* :doc:`logging` : Configuration du logging
