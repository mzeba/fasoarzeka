==========================
Authentification
==========================

Vue d'ensemble
==============

L'authentification est la première étape obligatoire pour utiliser l'API Faso Arzeka Payment.
Elle permet d'obtenir un **token d'accès JWT** (JSON Web Token) nécessaire pour effectuer toutes les opérations ultérieures.

Fonctionnement
--------------

Le processus d'authentification suit ce schéma :

1. **Envoi des identifiants** : Vous envoyez votre username et password à l'API
2. **Validation** : L'API vérifie vos identifiants
3. **Génération du token** : En cas de succès, l'API génère un token JWT
4. **Utilisation du token** : Vous utilisez ce token pour toutes vos requêtes suivantes

.. note::
   Les tokens JWT ont une durée de validité limitée (généralement 3600 secondes / 1 heure).
   Après expiration, vous devez vous réauthentifier.

Méthodes d'authentification
============================

Il existe deux façons de s'authentifier avec cette bibliothèque.

Méthode 1 : Fonction de convenance ``authenticate()``
------------------------------------------------------

C'est la méthode la plus simple pour une authentification rapide.

Signature
^^^^^^^^^

.. code-block:: python

   def authenticate(
       username: str,
       password: str,
       base_url: str = DEFAULT_BASE_URL
   ) -> Dict[str, Any]

Paramètres
^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Paramètre
     - Type
     - Description
   * - ``username``
     - ``str``
     - Votre identifiant utilisateur Arzeka (obligatoire)
   * - ``password``
     - ``str``
     - Votre mot de passe Arzeka (obligatoire)
   * - ``base_url``
     - ``str``
     - URL de base de l'API (optionnel, défaut : environnement de test)

Valeur de retour
^^^^^^^^^^^^^^^^

La fonction retourne un dictionnaire contenant :

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Champ
     - Type
     - Description
   * - ``access_token``
     - ``str``
     - Token JWT pour authentifier les requêtes suivantes
   * - ``token_type``
     - ``str``
     - Type de token, généralement ``"Bearer"``
   * - ``expires_in``
     - ``int``
     - Durée de validité du token en secondes

Exemple d'utilisation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from fasoarzeka import authenticate

   # S'authentifier
   auth = authenticate(
       username="votre_username",
       password="votre_password",
       base_url="https://pwg-test.fasoarzeka.com/"
   )

   # Afficher les informations
   print(f"Token : {auth['access_token']}")
   print(f"Type : {auth['token_type']}")
   print(f"Expire dans : {auth['expires_in']} secondes")

   # Extraire le token pour utilisation ultérieure
   token = auth['access_token']

Méthode 2 : Méthode de classe ``ArzekaPayment.authenticate()``
---------------------------------------------------------------

Cette méthode est intégrée à la classe ``ArzekaPayment`` et met automatiquement
à jour le token du client.

Signature
^^^^^^^^^

.. code-block:: python

   def authenticate(
       self,
       username: str,
       password: str
   ) -> Dict[str, Any]

Paramètres
^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Paramètre
     - Type
     - Description
   * - ``username``
     - ``str``
     - Votre identifiant utilisateur Arzeka
   * - ``password``
     - ``str``
     - Votre mot de passe Arzeka

Valeur de retour
^^^^^^^^^^^^^^^^

Retourne le même dictionnaire que la fonction de convenance, mais met également à jour :

- ``self._token`` : Le nouveau token d'accès
- ``self._expires_at`` : Timestamp d'expiration du token
- ``self._username`` : Username stocké pour réauthentification automatique
- ``self._password`` : Password stocké pour réauthentification automatique

Exemple d'utilisation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   # Créer le client sans token
   with ArzekaPayment(token="") as client:
       # S'authentifier
       auth = client.authenticate("votre_username", "votre_password")

       print(f"✅ Authentifié ! Token valide {auth['expires_in']}s")

       # Le client utilise maintenant automatiquement le token
       response = client.initiate_payment(
           amount=1000,
           merchant_id="MERCHANT_123",
           # ... autres paramètres
       )

Exemples pratiques
==================

Exemple 1 : Workflow complet (Authentification + Paiement)
-----------------------------------------------------------

.. code-block:: python

   from fasoarzeka import authenticate, initiate_payment

   # 1. S'authentifier pour obtenir le token
   auth = authenticate("user@example.com", "password123")
   token = auth['access_token']

   print(f"✅ Token obtenu, valide pendant {auth['expires_in']} secondes")

   # 2. Utiliser le token dans les opérations suivantes
   # (Le token est automatiquement utilisé par les fonctions de convenance)
   response = initiate_payment({
       "amount": 1000,
       "merchant_id": "MERCHANT_123",
       "additional_info": {
           "first_name": "Jean",
           "last_name": "Dupont",
           "mobile": "22670123456"
       },
       "mapped_order_id": "ORDER-001",
       "hash_secret": "votre_secret",
       "link_for_update_status": "https://exemple.com/webhook",
       "link_back_to_calling_website": "https://exemple.com/retour"
   })

   print(f"✅ Paiement initié : {response['url']}")

Exemple 2 : Authentification intégrée avec la classe
-----------------------------------------------------

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   # Le client s'authentifie et met à jour son token automatiquement
   with ArzekaPayment() as client:
       # S'authentifier
       auth = client.authenticate("user@example.com", "password123")

       print(f"Token type: {auth['token_type']}")
       print(f"Expires in: {auth['expires_in']}s")

       # Faire plusieurs opérations avec le même client
       response1 = client.initiate_payment(...)
       response2 = client.check_payment("ORDER-001")
       response3 = client.initiate_payment(...)

Exemple 3 : Gestion des erreurs d'authentification
---------------------------------------------------

.. code-block:: python

   from fasoarzeka import authenticate, ArzekaAuthenticationError

   try:
       auth = authenticate("user@example.com", "wrong_password")
       print(f"✅ Authentification réussie")

   except ArzekaAuthenticationError as e:
       print(f"❌ Échec de l'authentification : {e}")
       # Gérer l'erreur : afficher un message, demander de réessayer, etc.

Exemple 4 : Authentification avec configuration depuis l'environnement
-----------------------------------------------------------------------

.. code-block:: python

   import os
   from fasoarzeka import authenticate

   # Lire les identifiants depuis les variables d'environnement
   username = os.getenv('ARZEKA_USERNAME')
   password = os.getenv('ARZEKA_PASSWORD')
   base_url = os.getenv('ARZEKA_BASE_URL', 'https://pwg-test.fasoarzeka.com/')

   # Vérifier que les identifiants sont définis
   if not username or not password:
       raise ValueError("Variables ARZEKA_USERNAME et ARZEKA_PASSWORD requises")

   # S'authentifier
   auth = authenticate(username, password, base_url)
   print(f"✅ Authentification réussie")

Exemple 5 : Client long-running avec réauthentification
--------------------------------------------------------

.. code-block:: python

   import time
   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment()
   client.authenticate("username", "password")

   # Application qui tourne longtemps
   while True:
       try:
           # Vérifier si le token est toujours valide
           if not client.is_token_valid():
               print("⚠️ Token expiré, réauthentification...")
               client.authenticate("username", "password")

           # Faire des opérations
           status = client.check_payment("ORDER-001")
           print(f"Statut : {status['status']}")

           # Attendre avant la prochaine vérification
           time.sleep(300)  # 5 minutes

       except KeyboardInterrupt:
           print("Arrêt du client")
           client.close()
           break

Gestion du stockage des identifiants
=====================================

Pourquoi stocker les identifiants ?
------------------------------------

La bibliothèque stocke automatiquement votre username et password lors de l'authentification.
Cela permet la **réauthentification automatique** lorsque le token expire.

.. code-block:: python

   client = ArzekaPayment()

   # À l'authentification, les credentials sont stockés
   client.authenticate("username", "password")
   # → self._username = "username"
   # → self._password = "password"
   # → self._token = "eyJhbGciOiJIUz..."
   # → self._expires_at = 1709564421

   # Plus tard, si le token expire, réauthentification automatique
   response = client.initiate_payment(...)
   # → Vérifie is_token_valid()
   # → Si expiré, réauthentifie avec les credentials stockés
   # → Puis fait la requête

Sécurité des identifiants
--------------------------

.. danger::
   **Important** : Les identifiants sont stockés en mémoire pendant la durée de vie du client.

   - ✅ **Sécurisé** : Stockage en mémoire uniquement (non persisté sur disque)
   - ⚠️ **Attention** : Ne pas logger ou afficher les identifiants
   - ⚠️ **Attention** : Utiliser HTTPS en production
   - ✅ **Recommandé** : Utiliser des variables d'environnement

Bonnes pratiques de sécurité
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import os
   from fasoarzeka import ArzekaPayment

   # ✅ BON : Lire depuis les variables d'environnement
   client = ArzekaPayment()
   client.authenticate(
       os.getenv('ARZEKA_USERNAME'),
       os.getenv('ARZEKA_PASSWORD')
   )

   # ❌ MAUVAIS : Hard-coder les identifiants dans le code
   client.authenticate("username", "password")  # Ne pas faire ça !

Variables d'environnement
--------------------------

Définir les variables d'environnement :

**Bash / Zsh :**

.. code-block:: bash

   export ARZEKA_USERNAME="votre_username"
   export ARZEKA_PASSWORD="votre_password"
   export ARZEKA_BASE_URL="https://pwg-test.fasoarzeka.com/"

**Fichier .env :**

.. code-block:: text

   ARZEKA_USERNAME=votre_username
   ARZEKA_PASSWORD=votre_password
   ARZEKA_BASE_URL=https://pwg-test.fasoarzeka.com/

Puis avec python-dotenv :

.. code-block:: python

   from dotenv import load_dotenv
   import os
   from fasoarzeka import authenticate

   # Charger les variables depuis .env
   load_dotenv()

   # Utiliser les variables
   auth = authenticate(
       os.getenv('ARZEKA_USERNAME'),
       os.getenv('ARZEKA_PASSWORD'),
       os.getenv('ARZEKA_BASE_URL')
   )

Référence des erreurs d'authentification
=========================================

Exception ``ArzekaAuthenticationError``
---------------------------------------

Cette exception est levée en cas d'échec d'authentification.

Causes possibles
^^^^^^^^^^^^^^^^

1. **Identifiants incorrects**

   .. code-block:: python

      # Username ou password invalide
      auth = authenticate("wrong_user", "wrong_pass")
      # → ArzekaAuthenticationError: Authentication failed

2. **Compte verrouillé ou désactivé**

   .. code-block:: python

      # Compte bloqué par l'administrateur
      auth = authenticate("locked_user", "password")
      # → ArzekaAuthenticationError: Account locked

3. **Problème réseau**

   .. code-block:: python

      # Impossible de joindre l'API
      auth = authenticate("user", "pass")
      # → ArzekaConnectionError: Connection failed

Gestion des erreurs
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from fasoarzeka import (
       authenticate,
       ArzekaAuthenticationError,
       ArzekaConnectionError
   )

   max_retries = 3

   for attempt in range(max_retries):
       try:
           auth = authenticate("username", "password")
           print("✅ Authentification réussie")
           break

       except ArzekaAuthenticationError as e:
           print(f"❌ Authentification échouée : {e}")
           # Ne pas réessayer si les identifiants sont incorrects
           break

       except ArzekaConnectionError as e:
           print(f"⚠️ Erreur de connexion (tentative {attempt+1}/{max_retries})")
           if attempt < max_retries - 1:
               time.sleep(2)  # Attendre avant de réessayer

Résolution des problèmes courants
==================================

Problème : "Token expired"
---------------------------

**Cause** : Vous tentez d'utiliser un token expiré.

**Solution** : Réauthentifiez-vous ou utilisez la réauthentification automatique.

.. code-block:: python

   # Solution manuelle
   if not client.is_token_valid():
       client.authenticate("username", "password")

   # Solution automatique (recommandé)
   # La bibliothèque gère automatiquement la réauthentification
   response = client.initiate_payment(...)  # Auto re-auth si nécessaire

Problème : "Invalid credentials"
---------------------------------

**Cause** : Username ou password incorrect.

**Solution** : Vérifiez vos identifiants.

.. code-block:: python

   # Vérifier que les variables d'environnement sont correctement définies
   import os
   print(f"Username: {os.getenv('ARZEKA_USERNAME')}")
   # Ne jamais print le password !

Problème : SSL Certificate Error
---------------------------------

**Cause** : Problème de certificat SSL.

**Solution** : Mettre à jour les certificats ou désactiver la vérification (uniquement en test).

.. code-block:: python

   # En environnement de test seulement
   client = ArzekaPayment(verify_ssl=False)

Prochaines étapes
=================

Maintenant que vous maîtrisez l'authentification, explorez :

* :doc:`auto_reauth` : Réauthentification automatique
* :doc:`token_validation` : Validation et vérification des tokens
* :doc:`payments` : Guide complet des paiements
* :doc:`best_practices` : Bonnes pratiques de sécurité
