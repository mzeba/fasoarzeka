=================
Utilitaires
=================

La bibliothèque fournit plusieurs fonctions utilitaires dans le module ``fasoarzeka.utils``.

Vue d'ensemble
==============

.. code-block:: python

   from fasoarzeka import (
       format_msisdn,
       validate_phone_number,
       generate_hash_signature,
       get_reference,
       get_payment_request_id,
   )

format_msisdn()
===============

Formate un numéro de téléphone au format requis par l'API.

Signature
---------

.. code-block:: python

   def format_msisdn(phone: str) -> str

Paramètres
----------

* ``phone`` (str) : Numéro de téléphone à formater

Retour
------

* ``str`` : Numéro formaté (chiffres uniquement avec indicatif)

Exemples
--------

.. code-block:: python

   from fasoarzeka.utils import format_msisdn

   # Avec espaces
   phone = format_msisdn("226 70 12 34 56")
   print(phone)  # "22670123456"

   # Avec + et espaces
   phone = format_msisdn("+226 70 12 34 56")
   print(phone)  # "22670123456"

   # Avec tirets
   phone = format_msisdn("226-70-12-34-56")
   print(phone)  # "22670123456"

   # Déjà formaté
   phone = format_msisdn("22670123456")
   print(phone)  # "22670123456"

validate_phone_number()
=======================

Valide un numéro de téléphone.

Signature
---------

.. code-block:: python

   def validate_phone_number(phone: str) -> bool

Paramètres
----------

* ``phone`` (str) : Numéro de téléphone à valider

Retour
------

* ``bool`` : ``True`` si le numéro est valide, ``False`` sinon

Exemples
--------

.. code-block:: python

   from fasoarzeka.utils import validate_phone_number

   # Numéros valides
   is_valid = validate_phone_number("22670123456")
   print(is_valid)  # True

   is_valid = validate_phone_number("22650123456")
   print(is_valid)  # True

   # Numéros invalides
   is_valid = validate_phone_number("226701234")  # Trop court
   print(is_valid)  # False

   is_valid = validate_phone_number("12670123456")  # Mauvais indicatif
   print(is_valid)  # False

generate_hash_signature()
=========================

Calcule le ``hashString`` d'un paiement selon l'algorithme officiel de FASO ARZEKA.
``initiate_payment()`` l'appelle automatiquement : vous n'en avez besoin que pour
déboguer ou reproduire une signature.

Algorithme
----------

.. code-block:: text

   data       = "amount|merchantId|mappedOrderId|linkBackToCallingWebsite|linkForUpdateStatus|additionalInfo|hashSecret"
   hashString = base64( sha256( data en UTF-8 ) )

Signature
---------

.. code-block:: python

   def generate_hash_signature(
       hash_secret: str,
       amount: str,
       merchantId: str,
       mappedOrderId: str,
       linkBackToCallingWebsite: str,
       linkForUpdateStatus: str,
       additionalInfo: str,
   ) -> str

Les liens sont attendus **déjà encodés en Base64** et ``additionalInfo`` sous forme
de chaîne JSON, exactement comme ils sont envoyés à l'API.

Exemple
-------

.. code-block:: python

   import base64, json
   from fasoarzeka import generate_hash_signature

   hash_string = generate_hash_signature(
       hash_secret="my_secret_key",
       amount="1000",
       merchantId="1",
       mappedOrderId="9b1248cc-dad4-4f1e-baa1-16410de1ecec",
       linkBackToCallingWebsite=base64.b64encode(b"https://shop.example/retour").decode(),
       linkForUpdateStatus=base64.b64encode(b"https://shop.example/webhook").decode(),
       additionalInfo=json.dumps(
           {"firstname": "Test", "lastname": "Test", "mobile": "22612345678"},
           separators=(",", ":"),
       ),
   )

get_reference()
===============

Génère une référence de commande unique (UUID4, 36 caractères ; l'API accepte
jusqu'à 50). C'est la valeur utilisée comme ``mappedOrderId`` quand vous n'en
fournissez pas à ``initiate_payment()``.

.. code-block:: python

   from fasoarzeka import get_reference

   order_id = get_reference()
   print(order_id)  # "9b1248cc-dad4-4f1e-baa1-16410de1ecec"

get_payment_request_id()
========================

Extrait la référence de commande du retour sur le site marchand. Après le
paiement, la passerelle redirige vers ``link_back_to_calling_website`` avec
``?paymentRequestId=<mappedOrderId>`` (le nom est reconnu quelle que soit sa casse).

.. code-block:: python

   from fasoarzeka import get_payment_request_id

   get_payment_request_id("https://shop.example/retour?paymentRequestID=9b12")  # "9b12"
   get_payment_request_id({"paymentRequestId": "9b12"})                         # "9b12"
   get_payment_request_id("https://shop.example/retour")                         # None

.. warning::
   Cette valeur vient du navigateur et peut être falsifiée : confirmez toujours
   le paiement avec ``check_payment()``.

Exemples d'utilisation combinée
================================

Préparer un paiement
--------------------

.. code-block:: python

   from fasoarzeka import (
       ArzekaPayment,
       format_msisdn,
       get_reference,
       validate_phone_number,
   )

   def create_payment(client: ArzekaPayment, amount, phone, merchant_id, hash_secret):
       # Valider et formater le numéro
       if not validate_phone_number(phone):
           raise ValueError("Numéro de téléphone invalide")
       phone = format_msisdn(phone)

       # Générer une référence de commande
       order_id = get_reference()

       # Le hash est calculé automatiquement par initiate_payment()
       response, payment_data = client.initiate_payment(
           amount=amount,
           merchant_id=merchant_id,
           mapped_order_id=order_id,
           additional_info={
               "firstname": "Client",
               "lastname": "Test",
               "mobile": phone,
           },
           hash_secret=hash_secret,
           link_for_update_status="https://shop.example/webhook",
           link_back_to_calling_website="https://shop.example/retour",
       )
       return order_id, response["url"]

Voir aussi
==========

* :doc:`api_reference` : Référence API complète
* :doc:`quickstart` : Guide de démarrage rapide
