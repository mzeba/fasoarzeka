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
       base_url="https://pgw-test.fasoarzeka.bf/",
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
       amount: int | float | Decimal,
       merchant_id: str,
       link_for_update_status: str,
       link_back_to_calling_website: str,
       additional_info: Dict[str, Any],
       hash_secret: str,
       mapped_order_id: Optional[str] = None,
   ) -> Tuple[Dict[str, Any], Dict[str, Any]]

**Paramètres:**

* ``amount`` (int, float ou Decimal) : Montant en FCFA (minimum 100)
* ``merchant_id`` (str) : Identifiant marchand (20 caractères maximum)
* ``additional_info`` (dict) : Informations client. ``firstname``, ``lastname``
  et ``mobile`` sont obligatoires. Pour une quittance du Trésor :
  ``generateReceipt=True``, ``paymentDescription``, ``accountingOffice``,
  ``accountantName`` (``address`` facultatif). Le dict passé n'est pas modifié.
* ``hash_secret`` (str) : Clé secrète pour le hash
* ``link_for_update_status`` (str) : URL de votre backend appelée après le paiement
* ``link_back_to_calling_website`` (str) : URL de retour du navigateur après le paiement
* ``mapped_order_id`` (str, optionnel) : Référence de commande, 50 caractères
  maximum (UUID généré si absent)

**Retour:** Tuple ``(response, payment_data)`` :

* ``response`` : réponse de l'API, ``{"url": "<page de paiement>"}``
* ``payment_data`` : champs envoyés à l'API, dont ``mappedOrderId`` et ``hashString``

**Exceptions:**

* ``ArzekaValidationError`` : Données invalides
* ``ArzekaAuthenticationError`` : Token expiré ou invalide
* ``ArzekaAPIError`` : Erreur API
* ``ArzekaConnectionError`` : Problème de connexion

**Exemple:**

.. code-block:: python

   response, payment_data = client.initiate_payment(
       amount=1000,
       merchant_id="MERCHANT_123",
       additional_info={
           "firstname": "Jean",
           "lastname": "Dupont",
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

   def check_payment(self, mapped_order_id: str, transaction_id: str = None) -> Dict[str, Any]

**Paramètres:**

* ``mapped_order_id`` (str) : Référence de la commande
* ``transaction_id`` (str, optionnel) : Référence de la transaction de paiement

**Retour:** Dictionnaire avec ``status`` (voir :ref:`payment-status`), ``amount``,
``order_id``, ``merchant_id``, ``third_party_module``, ``third_party_trans_id``,
``created_at``, ``additionalInfo``…

**Exceptions:**

* ``ArzekaAuthenticationError`` : Token expiré ou invalide
* ``ArzekaAPIError`` : Erreur API (404 si commande introuvable)
* ``ArzekaConnectionError`` : Problème de connexion

**Exemple:**

.. code-block:: python

   from fasoarzeka import PaymentStatus

   status = client.check_payment("ORDER-2026-001")
   if status['status'] == PaymentStatus.COMPLETED:
       print("Paiement confirmé")

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

   def initiate_payment(payment_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]

**Paramètres:**

* ``payment_data`` (dict) : Dictionnaire contenant les paramètres de
  :meth:`ArzekaPayment.initiate_payment` (``amount``, ``merchant_id``…)

**Retour:** Tuple ``(response, payment_data)``, comme la méthode de classe

**Exemple:**

.. code-block:: python

   response, payment_data = initiate_payment({
       "amount": 1000,
       "merchant_id": "MERCHANT_123",
       # ... autres paramètres
   })

check_payment()
---------------

Fonction pour vérifier un paiement rapidement.

.. code-block:: python

   from fasoarzeka import check_payment

   def check_payment(mapped_order_id: str, transaction_id: str = None) -> Dict[str, Any]

**Paramètres:**

* ``mapped_order_id`` (str) : Référence de la commande
* ``transaction_id`` (str, optionnel) : Référence de la transaction de paiement

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

generate_hash_signature()
-------------------------

Calcule le ``hashString`` d'un paiement selon l'algorithme officiel :
``SHA256("amount|merchantId|mappedOrderId|linkBackToCallingWebsite|linkForUpdateStatus|additionalInfo|hashSecret")``
encodé en Base64. ``initiate_payment()`` l'appelle automatiquement.

.. code-block:: python

   from fasoarzeka import generate_hash_signature

   def generate_hash_signature(
       hash_secret: str,
       amount: str,
       merchantId: str,
       mappedOrderId: str,
       linkBackToCallingWebsite: str,
       linkForUpdateStatus: str,
       additionalInfo: str,
   ) -> str

Les liens sont attendus **déjà encodés en Base64** et ``additionalInfo`` sous
forme de chaîne JSON, exactement comme ils sont envoyés à l'API.

get_reference()
---------------

Génère une référence de commande unique (UUID4), utilisée comme
``mappedOrderId`` quand vous n'en fournissez pas.

.. code-block:: python

   from fasoarzeka import get_reference

   order_id = get_reference()
   # "9b1248cc-dad4-4f1e-baa1-16410de1ecec"

get_payment_request_id()
------------------------

Extrait la référence de commande du retour sur le site marchand
(``?paymentRequestId=...``, nom reconnu quelle que soit sa casse).

.. code-block:: python

   from fasoarzeka import get_payment_request_id

   def get_payment_request_id(query: str | Mapping[str, Any]) -> Optional[str]

**Paramètres:**

* ``query`` : URL complète, chaîne de requête, ou dictionnaire de paramètres
  (``request.args`` avec Flask, ``request.GET`` avec Django)

**Retour:** La référence (``mappedOrderId``), ou ``None`` si absente

.. warning::
   Cette valeur vient du navigateur et peut être falsifiée : confirmez
   toujours le paiement avec ``check_payment()``.

Constantes
==========

.. _payment-status:

PaymentStatus
-------------

Statuts renvoyés par ``check_payment()`` dans le champ ``status`` :

* ``PaymentStatus.COMPLETED`` (``"COMPLETED"``) : paiement réussi
* ``PaymentStatus.PENDING`` (``"PENDING"``) : paiement en cours
* ``PaymentStatus.INCOMPLETE`` (``"INCOMPLETE"``) : paiement non abouti
* ``PaymentStatus.ALL`` : les trois statuts

URL des environnements
----------------------

* ``TEST_BASE_URL`` : ``https://pgw-test.fasoarzeka.bf/`` (valeur par défaut)
* ``PRODUCTION_BASE_URL`` : ``https://pgw.fasoarzeka.bf/``

.. code-block:: python

   from fasoarzeka import PRODUCTION_BASE_URL, ArzekaPayment

   client = ArzekaPayment(base_url=PRODUCTION_BASE_URL)

Voir aussi
==========

* :doc:`exceptions` : Toutes les exceptions disponibles
* :doc:`best_practices` : Bonnes pratiques d'utilisation
* :doc:`quickstart` : Guide de démarrage rapide
