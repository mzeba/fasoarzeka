====================
Référence API
====================

Cette page fournit la documentation complète de toutes les classes, méthodes et fonctions disponibles.

Classes principales
===================

ArzekaPayment
-------------

Classe principale pour interagir avec l'API Faso Arzeka.

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment(
       token="",
       base_url="https://pwg-test.fasoarzeka.com/",
       timeout=30,
       max_retries=3,
       verify_ssl=True
   )

Paramètres du constructeur
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Paramètre
     - Type
     - Défaut
     - Description
   * - ``token``
     - ``str``
     - ``""``
     - Token d'authentification (peut être vide si vous appelez ``authenticate()``)
   * - ``base_url``
     - ``str``
     - Test URL
     - URL de base de l'API
   * - ``timeout``
     - ``int``
     - ``30``
     - Timeout des requêtes en secondes
   * - ``max_retries``
     - ``int``
     - ``3``
     - Nombre maximum de tentatives en cas d'échec
   * - ``verify_ssl``
     - ``bool``
     - ``True``
     - Vérifier les certificats SSL

Méthodes
^^^^^^^^

authenticate()
""""""""""""""

Authentifie l'utilisateur et obtient un token d'accès.

.. code-block:: python

   def authenticate(self, username: str, password: str) -> Dict[str, Any]

**Paramètres:**

* ``username`` (str) : Nom d'utilisateur Arzeka
* ``password`` (str) : Mot de passe Arzeka

**Retour:** Dictionnaire avec ``access_token``, ``token_type``, ``expires_in``

**Exceptions:**

* ``ArzekaAuthenticationError`` : Échec de l'authentification
* ``ArzekaConnectionError`` : Problème de connexion
* ``ArzekaAPIError`` : Erreur API

**Exemple:**

.. code-block:: python

   auth = client.authenticate("username", "password")
   print(auth['access_token'])

initiate_payment()
""""""""""""""""""

Initialise un nouveau paiement.

.. code-block:: python

   def initiate_payment(
       self,
       amount: int,
       merchant_id: str,
       additional_info: Dict[str, str],
       hash_secret: str,
       link_for_update_status: str,
       link_back_to_calling_website: str,
       mapped_order_id: Optional[str] = None,
       order_description: Optional[str] = None
   ) -> Dict[str, Any]

**Paramètres:**

* ``amount`` (int) : Montant en FCFA (minimum 100)
* ``merchant_id`` (str) : Identifiant marchand
* ``additional_info`` (dict) : Informations client (first_name, last_name, mobile)
* ``hash_secret`` (str) : Clé secrète pour le hash
* ``link_for_update_status`` (str) : URL du webhook
* ``link_back_to_calling_website`` (str) : URL de retour
* ``mapped_order_id`` (str, optionnel) : ID de commande personnalisé
* ``order_description`` (str, optionnel) : Description de la commande

**Retour:** Dictionnaire avec ``mappedOrderId``, ``url``, ``qrcode``, ``status``

**Exceptions:**

* ``ArzekaValidationError`` : Données invalides
* ``ArzekaAuthenticationError`` : Token expiré ou invalide
* ``ArzekaAPIError`` : Erreur API
* ``ArzekaConnectionError`` : Problème de connexion

**Exemple:**

.. code-block:: python

   response = client.initiate_payment(
       amount=1000,
       merchant_id="MERCHANT_123",
       additional_info={
           "first_name": "Jean",
           "last_name": "Dupont",
           "mobile": "22670123456"
       },
       hash_secret="secret",
       link_for_update_status="https://example.com/webhook",
       link_back_to_calling_website="https://example.com/return"
   )

check_payment()
"""""""""""""""

Vérifie le statut d'un paiement.

.. code-block:: python

   def check_payment(self, mapped_order_id: str) -> Dict[str, Any]

**Paramètres:**

* ``mapped_order_id`` (str) : ID de la commande

**Retour:** Dictionnaire avec ``mappedOrderId``, ``status``, ``amount``, ``orderDate``, etc.

**Exceptions:**

* ``ArzekaAuthenticationError`` : Token expiré ou invalide
* ``ArzekaAPIError`` : Erreur API (404 si commande introuvable)
* ``ArzekaConnectionError`` : Problème de connexion

**Exemple:**

.. code-block:: python

   status = client.check_payment("ORDER-2026-001")
   print(status['status'])

is_token_valid()
""""""""""""""""

Vérifie si le token est encore valide.

.. code-block:: python

   def is_token_valid(self, margin_seconds: int = 60) -> bool

**Paramètres:**

* ``margin_seconds`` (int) : Marge de sécurité en secondes (défaut : 60)

**Retour:** ``True`` si le token est valide, ``False`` sinon

**Exemple:**

.. code-block:: python

   if client.is_token_valid():
       print("Token valide")

get_token_expiry_info()
"""""""""""""""""""""""

Obtient des informations détaillées sur l'expiration du token.

.. code-block:: python

   def get_token_expiry_info(self) -> Dict[str, Any]

**Retour:** Dictionnaire avec ``is_valid``, ``expires_at``, ``seconds_remaining``, etc.

**Exemple:**

.. code-block:: python

   info = client.get_token_expiry_info()
   print(f"Expire dans {info['minutes_remaining']:.1f} minutes")

close()
"""""""

Ferme la session et libère les ressources.

.. code-block:: python

   def close(self) -> None

**Exemple:**

.. code-block:: python

   client.close()

Ou utilisez un context manager :

.. code-block:: python

   with ArzekaPayment() as client:
       # ... utiliser le client
       pass
   # close() appelé automatiquement

Fonctions de convenance
========================

authenticate()
--------------

Fonction pour s'authentifier rapidement.

.. code-block:: python

   from fasoarzeka import authenticate

   def authenticate(
       username: str,
       password: str,
       base_url: str = DEFAULT_BASE_URL
   ) -> Dict[str, Any]

**Paramètres:**

* ``username`` (str) : Nom d'utilisateur
* ``password`` (str) : Mot de passe
* ``base_url`` (str, optionnel) : URL de l'API

**Retour:** Dictionnaire d'authentification

**Exemple:**

.. code-block:: python

   auth = authenticate("username", "password")
   token = auth['access_token']

initiate_payment()
------------------

Fonction pour initier un paiement rapidement.

.. code-block:: python

   from fasoarzeka import initiate_payment

   def initiate_payment(payment_data: Dict[str, Any]) -> Dict[str, Any]

**Paramètres:**

* ``payment_data`` (dict) : Dictionnaire contenant tous les paramètres du paiement

**Retour:** Dictionnaire de réponse

**Exemple:**

.. code-block:: python

   response = initiate_payment({
       "amount": 1000,
       "merchant_id": "MERCHANT_123",
       # ... autres paramètres
   })

check_payment()
---------------

Fonction pour vérifier un paiement rapidement.

.. code-block:: python

   from fasoarzeka import check_payment

   def check_payment(mapped_order_id: str) -> Dict[str, Any]

**Paramètres:**

* ``mapped_order_id`` (str) : ID de la commande

**Retour:** Dictionnaire de statut

**Exemple:**

.. code-block:: python

   status = check_payment("ORDER-2026-001")

Utilitaires
===========

Module ``fasoarzeka.utils``

format_msisdn()
---------------

Formate un numéro de téléphone au format requis.

.. code-block:: python

   from fasoarzeka.utils import format_msisdn

   def format_msisdn(phone: str) -> str

**Paramètres:**

* ``phone`` (str) : Numéro de téléphone à formater

**Retour:** Numéro formaté (sans espaces, +, etc.)

**Exemple:**

.. code-block:: python

   phone = format_msisdn("+226 70 12 34 56")
   # Retourne: "22670123456"

validate_phone_number()
-----------------------

Valide un numéro de téléphone.

.. code-block:: python

   from fasoarzeka.utils import validate_phone_number

   def validate_phone_number(phone: str) -> bool

**Paramètres:**

* ``phone`` (str) : Numéro à valider

**Retour:** ``True`` si valide, ``False`` sinon

**Exemple:**

.. code-block:: python

   if validate_phone_number("22670123456"):
       print("Numéro valide")

generate_hash()
---------------

Génère un hash pour sécuriser les transactions.

.. code-block:: python

   from fasoarzeka.utils import generate_hash

   def generate_hash(
       mapped_order_id: str,
       amount: int,
       hash_secret: str
   ) -> str

**Paramètres:**

* ``mapped_order_id`` (str) : ID de commande
* ``amount`` (int) : Montant
* ``hash_secret`` (str) : Clé secrète

**Retour:** Hash calculé

**Exemple:**

.. code-block:: python

   hash_value = generate_hash("ORDER-001", 1000, "secret")

Voir aussi
==========

* :doc:`exceptions` : Toutes les exceptions disponibles
* :doc:`best_practices` : Bonnes pratiques d'utilisation
* :doc:`quickstart` : Guide de démarrage rapide
