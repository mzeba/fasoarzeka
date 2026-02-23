=================
Utilitaires
=================

La bibliothèque fournit plusieurs fonctions utilitaires dans le module ``fasoarzeka.utils``.

Vue d'ensemble
==============

.. code-block:: python

   from fasoarzeka.utils import (
       format_msisdn,
       validate_phone_number,
       generate_hash,
       generate_order_id
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

generate_hash()
===============

Génère un hash de sécurité pour les transactions.

Signature
---------

.. code-block:: python

   def generate_hash(
       mapped_order_id: str,
       amount: int,
       hash_secret: str
   ) -> str

Paramètres
----------

* ``mapped_order_id`` (str) : ID de la commande
* ``amount`` (int) : Montant de la transaction
* ``hash_secret`` (str) : Clé secrète

Retour
------

* ``str`` : Hash calculé (SHA-256)

Exemples
--------

.. code-block:: python

   from fasoarzeka.utils import generate_hash

   hash_value = generate_hash(
       mapped_order_id="ORDER-2026-001",
       amount=1000,
       hash_secret="my_secret_key"
   )
   print(hash_value)  # "a1b2c3d4e5f6..."

generate_order_id()
===================

Génère un ID de commande unique.

Signature
---------

.. code-block:: python

   def generate_order_id(prefix: str = "ORDER") -> str

Paramètres
----------

* ``prefix`` (str) : Préfixe de l'ID (défaut : "ORDER")

Retour
------

* ``str`` : ID unique généré

Exemples
--------

.. code-block:: python

   from fasoarzeka.utils import generate_order_id

   # Avec préfixe par défaut
   order_id = generate_order_id()
   print(order_id)  # "ORDER-20260223-103015-abc123"

   # Avec préfixe personnalisé
   order_id = generate_order_id(prefix="PAYMENT")
   print(order_id)  # "PAYMENT-20260223-103015-xyz789"

Exemples d'utilisation combinée
================================

Préparer un paiement
--------------------

.. code-block:: python

   from fasoarzeka import ArzekaPayment
   from fasoarzeka.utils import (
       format_msisdn,
       validate_phone_number,
       generate_hash,
       generate_order_id
   )

   def prepare_payment(amount, phone, merchant_id, hash_secret):
       # Valider et formater le numéro
       if not validate_phone_number(phone):
           raise ValueError("Numéro de téléphone invalide")

       phone = format_msisdn(phone)

       # Générer un ID de commande
       order_id = generate_order_id(prefix="PAY")

       # Générer le hash
       hash_value = generate_hash(order_id, amount, hash_secret)

       # Préparer les données
       payment_data = {
           "amount": amount,
           "merchant_id": merchant_id,
           "additional_info": {
               "first_name": "Client",
               "last_name": "Test",
               "mobile": phone
           },
           "mapped_order_id": order_id,
           "hash": hash_value,
           "hash_secret": hash_secret,
           # ... autres paramètres
       }

       return payment_data

   # Utilisation
   data = prepare_payment(
       amount=1000,
       phone="+226 70 12 34 56",
       merchant_id="MERCHANT_123",
       hash_secret="secret"
   )

Voir aussi
==========

* :doc:`api_reference` : Référence API complète
* :doc:`quickstart` : Guide de démarrage rapide
