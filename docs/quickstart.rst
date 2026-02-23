============================
Guide de démarrage rapide
============================

Ce guide vous apprendra les bases de l'utilisation de la bibliothèque Faso Arzeka Payment en quelques minutes.

Prérequis
=========

Avant de commencer, assurez-vous d'avoir :

1. Installé la bibliothèque (voir :doc:`installation`)
2. Obtenu vos identifiants API Arzeka :
   - Username
   - Password
   - Merchant ID
   - Hash Secret

Deux façons d'utiliser la bibliothèque
========================================

Il existe deux approches principales pour utiliser cette bibliothèque :

1. **Fonctions de convenance** (recommandé pour débuter)
2. **Instance de classe** (plus de flexibilité)

Option 1 : Fonctions de convenance
===================================

Cette approche est la plus simple pour démarrer rapidement.

Authentification
----------------

.. code-block:: python

   from fasoarzeka import authenticate

   # S'authentifier pour obtenir un token
   auth = authenticate(
       username="votre_username",
       password="votre_password",
       base_url="https://pwg-test.fasoarzeka.com/"
   )

   print(f"Token : {auth['access_token']}")
   print(f"Type : {auth['token_type']}")
   print(f"Expire dans : {auth['expires_in']} secondes")

Initier un paiement
-------------------

.. code-block:: python

   from fasoarzeka import initiate_payment

   # Préparer les données du paiement
   payment_data = {
       "amount": 1000,  # Montant en FCFA (minimum 100)
       "merchant_id": "MERCHANT_123",
       "additional_info": {
           "first_name": "Jean",
           "last_name": "Dupont",
           "mobile": "22670123456"  # Format : indicatif + numéro
       },
       "mapped_order_id": "ORDER-2026-001",  # ID unique de votre commande
       "hash_secret": "votre_hash_secret",
       "link_for_update_status": "https://votresite.com/webhook",
       "link_back_to_calling_website": "https://votresite.com/retour"
   }

   # Initier le paiement
   response = initiate_payment(payment_data)

   print(f"ID du paiement : {response['mappedOrderId']}")
   print(f"URL de redirection : {response['url']}")
   print(f"QR Code pour paiement : {response['qrcode']}")

Vérifier le statut d'un paiement
---------------------------------

.. code-block:: python

   from fasoarzeka import check_payment

   # Vérifier le statut avec l'ID de commande
   status = check_payment("ORDER-2026-001")

   print(f"Statut : {status['status']}")
   print(f"Montant : {status['amount']} FCFA")
   print(f"Date : {status['orderDate']}")

Exemple complet
---------------

.. code-block:: python

   from fasoarzeka import authenticate, initiate_payment, check_payment

   # 1. S'authentifier
   auth = authenticate("votre_username", "votre_password")
   print(f"✅ Authentifié ! Token valide {auth['expires_in']}s")

   # 2. Initier un paiement
   payment_data = {
       "amount": 1000,
       "merchant_id": "MERCHANT_123",
       "additional_info": {
           "first_name": "Jean",
           "last_name": "Dupont",
           "mobile": "22670123456"
       },
       "mapped_order_id": "ORDER-2026-001",
       "hash_secret": "votre_secret",
       "link_for_update_status": "https://exemple.com/webhook",
       "link_back_to_calling_website": "https://exemple.com/retour"
   }

   response = initiate_payment(payment_data)
   print(f"✅ Paiement initié : {response['url']}")

   # 3. Vérifier le statut (après que l'utilisateur ait payé)
   import time
   time.sleep(5)  # Attendre quelques secondes
   status = check_payment("ORDER-2026-001")
   print(f"✅ Statut : {status['status']}")

Option 2 : Instance de classe
==============================

Cette approche offre plus de contrôle et est recommandée pour les applications en production.

Utilisation avec Context Manager
---------------------------------

Le context manager gère automatiquement l'ouverture et la fermeture de la session :

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   with ArzekaPayment(base_url="https://pwg-test.fasoarzeka.com/") as client:
       # 1. S'authentifier
       auth = client.authenticate("votre_username", "votre_password")

       # 2. Initier un paiement
       response = client.initiate_payment(
           amount=1000,
           merchant_id="MERCHANT_123",
           additional_info={
               "first_name": "Jean",
               "last_name": "Dupont",
               "mobile": "22670123456"
           },
           mapped_order_id="ORDER-2026-001",
           hash_secret="votre_secret",
           link_for_update_status="https://exemple.com/webhook",
           link_back_to_calling_website="https://exemple.com/retour"
       )

       print(f"Paiement initié : {response['url']}")

       # 3. Vérifier le statut
       status = client.check_payment("ORDER-2026-001")
       print(f"Statut : {status['status']}")

Utilisation sans Context Manager
---------------------------------

Si vous préférez gérer manuellement le cycle de vie du client :

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   # Créer le client
   client = ArzekaPayment(base_url="https://pwg-test.fasoarzeka.com/")

   try:
       # S'authentifier
       auth = client.authenticate("votre_username", "votre_password")

       # Faire des opérations
       response = client.initiate_payment(...)

   finally:
       # Toujours fermer le client
       client.close()

Gestion des erreurs
===================

La bibliothèque fournit des exceptions personnalisées pour différents types d'erreurs.

Exceptions disponibles
----------------------

.. code-block:: python

   from fasoarzeka import (
       ArzekaPaymentError,         # Exception de base
       ArzekaValidationError,      # Erreur de validation des données
       ArzekaAuthenticationError,  # Erreur d'authentification
       ArzekaAPIError,             # Erreur retournée par l'API
       ArzekaConnectionError,      # Erreur de connexion réseau
       ArzekaTimeoutError         # Timeout de la requête
   )

Exemple avec gestion d'erreurs
-------------------------------

.. code-block:: python

   from fasoarzeka import (
       ArzekaPayment,
       ArzekaValidationError,
       ArzekaAuthenticationError,
       ArzekaAPIError,
       ArzekaConnectionError
   )

   with ArzekaPayment() as client:
       try:
           # S'authentifier
           auth = client.authenticate("username", "password")

           # Initier un paiement
           response = client.initiate_payment(
               amount=1000,
               merchant_id="MERCHANT_123",
               additional_info={
                   "first_name": "Jean",
                   "last_name": "Dupont",
                   "mobile": "22670123456"
               },
               mapped_order_id="ORDER-2026-001",
               hash_secret="secret",
               link_for_update_status="https://exemple.com/webhook",
               link_back_to_calling_website="https://exemple.com/retour"
           )

           print(f"✅ Succès : {response['url']}")

       except ArzekaAuthenticationError as e:
           print(f"❌ Échec de l'authentification : {e}")

       except ArzekaValidationError as e:
           print(f"❌ Données invalides : {e}")

       except ArzekaAPIError as e:
           print(f"❌ Erreur API (code {e.status_code}) : {e}")
           print(f"Détails : {e.response_data}")

       except ArzekaConnectionError as e:
           print(f"❌ Erreur de connexion : {e}")

Fonctionnalités utiles
=======================

Formatage des numéros de téléphone
-----------------------------------

.. code-block:: python

   from fasoarzeka.utils import format_msisdn, validate_phone_number

   # Formater un numéro (retire espaces, +, etc.)
   phone = format_msisdn("+226 70 12 34 56")
   print(phone)  # "22670123456"

   # Valider un numéro
   is_valid = validate_phone_number("22670123456")
   print(is_valid)  # True

Génération du Hash
------------------

.. code-block:: python

   from fasoarzeka.utils import generate_hash

   hash_value = generate_hash(
       mapped_order_id="ORDER-2026-001",
       amount=1000,
       hash_secret="votre_secret"
   )
   print(f"Hash : {hash_value}")

Configuration du Logging
-------------------------

.. code-block:: python

   import logging
   from fasoarzeka import ArzekaPayment

   # Activer les logs détaillés
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

   # Les requêtes et réponses seront loggées
   with ArzekaPayment() as client:
       client.authenticate("username", "password")

Exemples pratiques
==================

Exemple 1 : Paiement simple
----------------------------

.. code-block:: python

   from fasoarzeka import authenticate, initiate_payment

   # Authentifier
   auth = authenticate("username", "password")

   # Préparer et envoyer le paiement
   response = initiate_payment({
       "amount": 1000,
       "merchant_id": "MERCHANT_123",
       "additional_info": {
           "first_name": "Marie",
           "last_name": "Kaboré",
           "mobile": "22670123456"
       },
       "mapped_order_id": "ORDER-001",
       "hash_secret": "secret",
       "link_for_update_status": "https://shop.com/webhook",
       "link_back_to_calling_website": "https://shop.com/success"
   })

   # Rediriger l'utilisateur vers l'URL de paiement
   print(f"Redirigez vers : {response['url']}")

Exemple 2 : Vérification périodique du statut
----------------------------------------------

.. code-block:: python

   import time
   from fasoarzeka import check_payment

   order_id = "ORDER-001"
   max_attempts = 10

   for attempt in range(max_attempts):
       status = check_payment(order_id)

       if status['status'] == 'COMPLETED':
           print("✅ Paiement réussi !")
           break
       elif status['status'] == 'FAILED':
           print("❌ Paiement échoué")
           break
       else:
           print(f"⏳ En attente... (tentative {attempt + 1}/{max_attempts})")
           time.sleep(5)  # Attendre 5 secondes

Exemple 3 : Application web Flask
----------------------------------

.. code-block:: python

   from flask import Flask, request, redirect, jsonify
   from fasoarzeka import ArzekaPayment

   app = Flask(__name__)
   client = ArzekaPayment()

   @app.route('/payer', methods=['POST'])
   def create_payment():
       # Authentifier si nécessaire
       if not client.is_token_valid():
           client.authenticate("username", "password")

       # Récupérer les données du formulaire
       data = request.json

       # Initier le paiement
       response = client.initiate_payment(
           amount=data['amount'],
           merchant_id="MERCHANT_123",
           additional_info={
               "first_name": data['first_name'],
               "last_name": data['last_name'],
               "mobile": data['mobile']
           },
           mapped_order_id=data['order_id'],
           hash_secret="votre_secret",
           link_for_update_status="https://votresite.com/webhook",
           link_back_to_calling_website="https://votresite.com/success"
       )

       # Retourner l'URL de paiement
       return jsonify({
           'payment_url': response['url'],
           'order_id': response['mappedOrderId']
       })

   @app.route('/webhook', methods=['POST'])
   def webhook():
       # Recevoir la notification de paiement
       data = request.json
       order_id = data.get('mappedOrderId')

       # Vérifier le statut
       status = client.check_payment(order_id)

       # Mettre à jour votre base de données
       # ...

       return jsonify({'status': 'received'})

   if __name__ == '__main__':
       app.run(debug=True)

Prochaines étapes
=================

Maintenant que vous maîtrisez les bases, explorez :

* :doc:`authentication` : Comprendre l'authentification en détail
* :doc:`payments` : Guide complet des paiements
* :doc:`auto_reauth` : Réauthentification automatique
* :doc:`token_validation` : Validation et gestion des tokens
* :doc:`api_reference` : Référence complète de l'API
* :doc:`best_practices` : Bonnes pratiques et recommandations
