======================
Paiements
======================

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

   response, payment_data = initiate_payment({
       "amount": 1000,
       "merchant_id": "MERCHANT_123",
       "additional_info": {
           "firstname": "Jean",
           "lastname": "Dupont",
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

       response, payment_data = client.initiate_payment(
           amount=1000,
           merchant_id="MERCHANT_123",
           additional_info={
               "firstname": "Jean",
               "lastname": "Dupont",
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
     - Informations du client (firstname, lastname, mobile)
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
     - Référence unique de votre commande, 50 caractères maximum
       (UUID généré automatiquement si absent)

Pour obtenir une quittance du Trésor, ajoutez dans ``additional_info`` :
``generateReceipt: True``, ``paymentDescription``, ``accountingOffice`` et
``accountantName`` (``address`` est facultatif).

Valeur de retour
----------------

``initiate_payment()`` renvoie un **tuple** ``(response, payment_data)`` :

* ``response`` : la réponse de l'API, qui contient uniquement l'URL de la page
  de paiement vers laquelle rediriger le navigateur de l'utilisateur ;
* ``payment_data`` : les données envoyées à l'API, dont ``mappedOrderId``
  (à conserver pour vérifier le paiement) et ``hashString``.

.. code-block:: python

   response, payment_data = client.initiate_payment(...)

   response
   # {"url": "https://pgw-test.fasoarzeka.bf/AvepayPaymentGatewayUI/avepay-payment/app/initializePayment?id=a58b81bb-..."}

   payment_data["mappedOrderId"]
   # "9b1248cc-dad4-4f1e-baa1-16410de1ecec"

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
       response, payment_data = client.initiate_payment(
           amount=5000,  # 5000 FCFA
           merchant_id="MERCHANT_123",
           additional_info={
               "firstname": "Marie",
               "lastname": "Kaboré",
               "mobile": "22670123456",
               "email": "marie@example.com"  # Optionnel
           },
           mapped_order_id=order_id,
           hash_secret="votre_hash_secret",
           link_for_update_status="https://monsite.com/api/webhook",
           link_back_to_calling_website="https://monsite.com/success"
       )

       # Afficher l'URL de paiement
       print(f"Redirigez l'utilisateur vers : {response['url']}")

       # Stocker la référence dans votre base de données
       # save_to_database(payment_data["mappedOrderId"], response["url"])

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
     - La référence de commande (``payment_data["mappedOrderId"]``)
   * - ``transaction_id``
     - ``str``, optionnel
     - Référence de la transaction de paiement (``transId``)

Réponse de l'API
----------------

.. code-block:: python

   {
       "id": 12960,
       "order_id": "714ceca9-2a0a-423a-8700-bda1df8ac641",
       "merchant_id": "1",
       "status": "COMPLETED",
       "third_party_module": "...",          # moyen de paiement utilisé
       "third_party_mapped_order_id": "9ee6f3e4-c4d6-4859-b11d-ccfd1e45e258",
       "third_party_redirect_url": "...",
       "third_party_trans_id": "...",
       "created_at": "2025-07-11",
       "amount": "1000",
       "additionalInfo": "{\"firstname\":\"Test\",\"lastname\":\"Test\",\"mobile\":\"22612345678\"}"
   }

Une commande inconnue lève ``ArzekaAPIError`` avec ``status_code == 404``.

Statuts possibles
-----------------

Utilisez les constantes de :class:`fasoarzeka.PaymentStatus` :

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Statut
     - Description
   * - ``PaymentStatus.COMPLETED``
     - Paiement réussi
   * - ``PaymentStatus.PENDING``
     - Paiement en cours
   * - ``PaymentStatus.INCOMPLETE``
     - Paiement non abouti (abandonné ou échoué)

Exemple de vérification périodique
-----------------------------------

.. code-block:: python

   import time
   from fasoarzeka import PaymentStatus, check_payment

   def wait_for_payment(order_id, max_attempts=20, delay=5):
       """Attendre qu'un paiement soit complété"""
       for attempt in range(max_attempts):
           status = check_payment(order_id)

           if status['status'] == PaymentStatus.COMPLETED:
               print("✅ Paiement réussi !")
               return status
           elif status['status'] == PaymentStatus.INCOMPLETE:
               print("❌ Paiement non abouti")
               return status
           else:
               print(f"⏳ En attente... (tentative {attempt + 1}/{max_attempts})")
               time.sleep(delay)

       print("⏱️ Timeout : Paiement toujours en attente")
       return None

   # Utilisation
   result = wait_for_payment("ORDER-2026-001")

Retour sur le site marchand
===========================

Après le paiement, la passerelle redirige le navigateur de l'utilisateur vers
``link_back_to_calling_website`` en ajoutant la référence de commande :

.. code-block:: text

   GET <link_back_to_calling_website>?paymentRequestId=9b1248cc-dad4-4f1e-baa1-16410de1ecec

``get_payment_request_id()`` extrait cette référence (le nom du paramètre est
reconnu quelle que soit sa casse : ``paymentRequestId`` ou ``paymentRequestID``) :

.. code-block:: python

   from flask import Flask, request
   from fasoarzeka import PaymentStatus, check_payment, get_payment_request_id

   app = Flask(__name__)

   @app.route('/retour')
   def retour_paiement():
       order_id = get_payment_request_id(request.args)   # ou request.url
       if order_id is None:
           return "Référence de paiement absente", 400

       # Le paramètre vient du navigateur et peut être falsifié :
       # toujours confirmer côté serveur.
       status = check_payment(order_id)
       if status['status'] == PaymentStatus.COMPLETED:
           return "Merci, paiement confirmé !"
       return "Paiement non confirmé"

.. warning::
   Ne vous fiez jamais uniquement aux paramètres de l'URL de retour : ils
   peuvent être manipulés. Vérifiez toujours le paiement avec ``check_payment()``.

Notification serveur (``link_for_update_status``)
=================================================

``link_for_update_status`` est l'URL de votre backend que la passerelle appelle
après le paiement.

.. note::
   La documentation officielle de FASO ARZEKA **ne décrit pas le contenu** de
   cet appel. Ne dépendez donc pas de son format : placez vous-même la
   référence de commande dans l'URL, puis vérifiez le statut avec
   ``check_payment()``.

Configuration
-------------

.. code-block:: python

   from urllib.parse import quote
   from fasoarzeka import get_reference

   order_id = get_reference()
   response, payment_data = client.initiate_payment(
       # ... autres paramètres
       mapped_order_id=order_id,
       link_for_update_status=f"https://monsite.com/api/arzeka/webhook?order={quote(order_id)}"
   )

Exemple d'implémentation Flask
-------------------------------

.. code-block:: python

   from flask import Flask, request, jsonify
   from fasoarzeka import PaymentStatus, check_payment

   app = Flask(__name__)

   @app.route('/api/arzeka/webhook', methods=['GET', 'POST'])
   def arzeka_webhook():
       # Référence placée par vous dans link_for_update_status
       order_id = request.args.get('order')
       if not order_id:
           return jsonify({'status': 'ignored'}), 400

       # Vérifier le statut auprès d'Arzeka (sécurité)
       verified_status = check_payment(order_id)

       if verified_status['status'] == PaymentStatus.COMPLETED:
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
   from fasoarzeka import PaymentStatus, check_payment

   @csrf_exempt
   def arzeka_webhook(request):
       # Référence placée par vous dans link_for_update_status
       order_id = request.GET.get('order')
       if not order_id:
           return JsonResponse({'status': 'ignored'}, status=400)

       # Vérifier le statut
       verified_status = check_payment(order_id)

       if verified_status['status'] == PaymentStatus.COMPLETED:
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
2. **Idempotence** : Gérer les notifications en double
3. **Retourner 200 OK** : Retourner rapidement une réponse HTTP 200

.. code-block:: python

   @app.route('/webhook', methods=['GET', 'POST'])
   def webhook():
       order_id = request.args.get('order')

       # Vérifier si déjà traité (idempotence)
       if is_already_processed(order_id):
           return jsonify({'status': 'already_processed'}), 200

       # Vérifier le statut auprès d'Arzeka
       verified = check_payment(order_id)

       if verified['status'] == PaymentStatus.COMPLETED:
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
           response, payment_data = client.initiate_payment(
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
