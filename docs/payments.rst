========
Paiements
========

Ce guide couvre toutes les opérations liées aux paiements : initiation, vérification de statut, et gestion des webhooks.

Vue d'ensemble
==============

Le processus de paiement Faso Arzeka se déroule en plusieurs étapes :

1. **Initier le paiement** : Créer une transaction et obtenir une URL de paiement
2. **Rediriger l'utilisateur** : L'utilisateur est redirigé vers la passerelle de paiement
3. **Paiement** : L'utilisateur effectue le paiement via Mobile Money
4. **Notification** : Arzeka envoie une notification à votre webhook (optionnel)
5. **Vérification** : Vous vérifiez le statut du paiement

Initier un paiement
===================

Deux méthodes pour initier un paiement
---------------------------------------

**Méthode 1 : Fonction de convenance**

.. code-block:: python

   from fasoarzeka import initiate_payment

   response = initiate_payment({
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
   })

**Méthode 2 : Méthode de classe**

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   with ArzekaPayment() as client:
       client.authenticate("username", "password")

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

Paramètres requis
-----------------

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Paramètre
     - Type
     - Description
   * - ``amount``
     - ``int``
     - Montant en FCFA (minimum 100, maximum selon votre contrat)
   * - ``merchant_id``
     - ``str``
     - Votre identifiant marchand unique
   * - ``additional_info``
     - ``dict``
     - Informations du client (first_name, last_name, mobile)
   * - ``hash_secret``
     - ``str``
     - Votre clé secrète pour la génération de hash
   * - ``link_for_update_status``
     - ``str``
     - URL de votre webhook pour recevoir les notifications
   * - ``link_back_to_calling_website``
     - ``str``
     - URL de retour après le paiement

Paramètres optionnels
---------------------

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Paramètre
     - Type
     - Description
   * - ``mapped_order_id``
     - ``str``
     - ID unique de votre commande (généré automatiquement si absent)
   * - ``order_description``
     - ``str``
     - Description de la commande

Réponse de l'API
----------------

Un dictionnaire contenant :

.. code-block:: python

   {
       "mappedOrderId": "ORDER-2026-001",
       "url": "https://pwg.fasoarzeka.com/payment/abc123",
       "qrcode": "data:image/png;base64,iVBORw0KGgo...",
       "status": "PENDING"
   }

Exemple complet
---------------

.. code-block:: python

   from fasoarzeka import ArzekaPayment
   import uuid

   with ArzekaPayment() as client:
       # Authentification
       client.authenticate("username", "password")

       # Générer un ID de commande unique
       order_id = f"ORDER-{uuid.uuid4().hex[:10]}"

       # Initier le paiement
       response = client.initiate_payment(
           amount=5000,  # 5000 FCFA
           merchant_id="MERCHANT_123",
           additional_info={
               "first_name": "Marie",
               "last_name": "Kaboré",
               "mobile": "22670123456",
               "email": "marie@example.com"  # Optionnel
           },
           mapped_order_id=order_id,
           order_description="Achat de produits",
           hash_secret="votre_hash_secret",
           link_for_update_status="https://monsite.com/api/webhook",
           link_back_to_calling_website="https://monsite.com/success"
       )

       # Afficher l'URL de paiement
       print(f"Redirigez l'utilisateur vers : {response['url']}")

       # Stocker l'order_id dans votre base de données
       # save_to_database(order_id, response)

Vérifier un paiement
====================

Après avoir initié un paiement, vous pouvez vérifier son statut.

Deux méthodes pour vérifier
----------------------------

**Méthode 1 : Fonction de convenance**

.. code-block:: python

   from fasoarzeka import check_payment

   status = check_payment("ORDER-2026-001")
   print(f"Statut : {status['status']}")

**Méthode 2 : Méthode de classe**

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   with ArzekaPayment() as client:
       client.authenticate("username", "password")
       status = client.check_payment("ORDER-2026-001")

Paramètres
----------

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Paramètre
     - Type
     - Description
   * - ``mapped_order_id``
     - ``str``
     - L'ID de commande retourné lors de l'initiation

Réponse de l'API
----------------

.. code-block:: python

   {
       "mappedOrderId": "ORDER-2026-001",
       "status": "COMPLETED",  # ou PENDING, FAILED, CANCELLED
       "amount": 1000,
       "orderDate": "2026-02-23T10:30:00",
       "paymentDate": "2026-02-23T10:35:00",
       "transactionId": "TX123456789"
   }

Statuts possibles
-----------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Statut
     - Description
   * - ``PENDING``
     - Paiement en attente, l'utilisateur n'a pas encore payé
   * - ``COMPLETED``
     - Paiement réussi et confirmé
   * - ``FAILED``
     - Paiement échoué (fonds insuffisants, annulation, etc.)
   * - ``CANCELLED``
     - Paiement annulé par l'utilisateur ou le système

Exemple de vérification périodique
-----------------------------------

.. code-block:: python

   import time
   from fasoarzeka import check_payment

   def wait_for_payment(order_id, max_attempts=20, delay=5):
       """Attendre qu'un paiement soit complété"""
       for attempt in range(max_attempts):
           status = check_payment(order_id)

           if status['status'] == 'COMPLETED':
               print("✅ Paiement réussi !")
               return status
           elif status['status'] == 'FAILED':
               print("❌ Paiement échoué")
               return status
           elif status['status'] == 'CANCELLED':
               print("⚠️ Paiement annulé")
               return status
           else:
               print(f"⏳ En attente... (tentative {attempt + 1}/{max_attempts})")
               time.sleep(delay)

       print("⏱️ Timeout : Paiement toujours en attente")
       return None

   # Utilisation
   result = wait_for_payment("ORDER-2026-001")

Webhooks
========

Les webhooks permettent de recevoir des notifications en temps réel lorsque le statut d'un paiement change.

Configuration du webhook
-------------------------

Lors de l'initiation du paiement, spécifiez l'URL de votre webhook :

.. code-block:: python

   response = client.initiate_payment(
       # ... autres paramètres
       link_for_update_status="https://monsite.com/api/arzeka/webhook"
   )

Format de la notification
--------------------------

Arzeka envoie une requête POST à votre URL avec ce format :

.. code-block:: json

   {
       "mappedOrderId": "ORDER-2026-001",
       "status": "COMPLETED",
       "amount": 1000,
       "transactionId": "TX123456789",
       "paymentDate": "2026-02-23T10:35:00"
   }

Exemple d'implémentation Flask
-------------------------------

.. code-block:: python

   from flask import Flask, request, jsonify
   from fasoarzeka import check_payment

   app = Flask(__name__)

   @app.route('/api/arzeka/webhook', methods=['POST'])
   def arzeka_webhook():
       # Récupérer les données
       data = request.json
       order_id = data.get('mappedOrderId')
       status = data.get('status')

       # Vérifier le statut auprès d'Arzeka (sécurité)
       verified_status = check_payment(order_id)

       if verified_status['status'] == 'COMPLETED':
           # Mettre à jour votre base de données
           update_order_status(order_id, 'PAID')

           # Envoyer un email de confirmation
           send_confirmation_email(order_id)

           print(f"✅ Paiement {order_id} confirmé")

       # Retourner une réponse 200 OK
       return jsonify({'status': 'received'}), 200

   if __name__ == '__main__':
       app.run(port=5000)

Exemple d'implémentation Django
--------------------------------

.. code-block:: python

   from django.http import JsonResponse
   from django.views.decorators.csrf import csrf_exempt
   from django.views.decorators.http import require_POST
   from fasoarzeka import check_payment
   import json

   @csrf_exempt
   @require_POST
   def arzeka_webhook(request):
       # Récupérer les données
       data = json.loads(request.body)
       order_id = data.get('mappedOrderId')

       # Vérifier le statut
       verified_status = check_payment(order_id)

       if verified_status['status'] == 'COMPLETED':
           # Mettre à jour la commande
           order = Order.objects.get(order_id=order_id)
           order.status = 'PAID'
           order.save()

       return JsonResponse({'status': 'received'})

Sécurité des webhooks
----------------------

.. warning::
   **Important** : Toujours vérifier le statut auprès d'Arzeka avant de valider la commande !

Bonnes pratiques :

1. **Vérifier le statut** : Appelez ``check_payment()`` pour confirmer
2. **Valider le hash** : Vérifiez le hash si fourni par Arzeka
3. **Idempotence** : Gérer les notifications en double
4. **Retourner 200 OK** : Retourner rapidement une réponse HTTP 200

.. code-block:: python

   @app.route('/webhook', methods=['POST'])
   def webhook():
       data = request.json
       order_id = data.get('mappedOrderId')

       # Vérifier si déjà traité (idempotence)
       if is_already_processed(order_id):
           return jsonify({'status': 'already_processed'}), 200

       # Vérifier le statut auprès d'Arzeka
       verified = check_payment(order_id)

       if verified['status'] == 'COMPLETED':
           # Traiter le paiement
           process_payment(order_id)
           mark_as_processed(order_id)

       return jsonify({'status': 'received'}), 200

Gestion des erreurs
===================

Exception lors de l'initiation
-------------------------------

.. code-block:: python

   from fasoarzeka import (
       ArzekaPayment,
       ArzekaValidationError,
       ArzekaAPIError
   )

   with ArzekaPayment() as client:
       client.authenticate("username", "password")

       try:
           response = client.initiate_payment(
               amount=1000,
               merchant_id="MERCHANT_123",
               # ... paramètres
           )
       except ArzekaValidationError as e:
           print(f"❌ Données invalides : {e}")
       except ArzekaAPIError as e:
           print(f"❌ Erreur API : {e}")
           print(f"Code : {e.status_code}")
           print(f"Détails : {e.response_data}")

Exception lors de la vérification
----------------------------------

.. code-block:: python

   from fasoarzeka import check_payment, ArzekaAPIError

   try:
       status = check_payment("ORDER-2026-001")
   except ArzekaAPIError as e:
       if e.status_code == 404:
           print("❌ Commande introuvable")
       else:
           print(f"❌ Erreur : {e}")

Bonnes pratiques
================

1. **IDs uniques**

   Toujours générer des IDs de commande uniques :

   .. code-block:: python

      import uuid
      from datetime import datetime

      # Option 1 : UUID
      order_id = f"ORDER-{uuid.uuid4().hex[:10]}"

      # Option 2 : Timestamp + aléatoire
      order_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"

2. **Timeout approprié**

   Configurez un timeout adapté :

   .. code-block:: python

      client = ArzekaPayment(timeout=30)  # 30 secondes

3. **Retry avec backoff**

   La bibliothèque gère automatiquement les retries, mais vous pouvez configurer :

   .. code-block:: python

      client = ArzekaPayment(max_retries=3, retry_delay=2)

4. **Logging**

   Activez le logging pour déboguer :

   .. code-block:: python

      import logging
      logging.basicConfig(level=logging.DEBUG)

5. **Validation des données**

   Validez les données avant de les envoyer :

   .. code-block:: python

      from fasoarzeka.utils import validate_phone_number

      if not validate_phone_number(mobile):
          raise ValueError("Numéro de téléphone invalide")

Prochaines étapes
=================

* :doc:`auto_reauth` : Réauthentification automatique
* :doc:`error_handling` : Gestion avancée des erreurs
* :doc:`best_practices` : Bonnes pratiques et recommandations
* :doc:`api_reference` : Référence complète de l'API
