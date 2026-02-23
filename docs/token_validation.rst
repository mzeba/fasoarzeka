==================
Validation des tokens
==================

La bibliothèque fournit des méthodes pour vérifier la validité des tokens d'authentification
et obtenir des informations détaillées sur leur expiration.

Vue d'ensemble
==============

Deux méthodes principales sont disponibles :

1. **``is_token_valid()``** : Vérification simple (retourne ``bool``)
2. **``get_token_expiry_info()``** : Informations détaillées (retourne ``dict``)

Ces méthodes permettent de :

* Vérifier si un token est encore valide
* Connaître le temps restant avant expiration
* Anticiper la réauthentification
* Gérer les tokens de manière proactive

Méthode ``is_token_valid()``
=============================

Cette méthode effectue une vérification simple de la validité du token.

Signature
---------

.. code-block:: python

   def is_token_valid(self, margin_seconds: int = 60) -> bool

Paramètres
----------

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Paramètre
     - Type
     - Description
   * - ``margin_seconds``
     - ``int``
     - Marge de sécurité en secondes avant l'expiration réelle (défaut : 60)

Le paramètre ``margin_seconds`` permet de considérer le token comme expiré quelques secondes
avant son expiration réelle. Cela évite les situations où le token expire **pendant** une requête.

Valeur de retour
----------------

* ``True`` : Le token est valide et n'expirera pas dans les ``margin_seconds`` prochaines secondes
* ``False`` : Le token est expiré, inexistant, ou expirera bientôt

Exemples d'utilisation
-----------------------

Exemple 1 : Vérification basique
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment()
   client.authenticate("username", "password")

   # Vérification simple
   if client.is_token_valid():
       print("✅ Token valide, vous pouvez faire des opérations")
   else:
       print("❌ Token expiré, réauthentification nécessaire")

Exemple 2 : Avec marge de sécurité personnalisée
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Vérifier si le token est valide pour au moins 5 minutes
   if client.is_token_valid(margin_seconds=300):
       print("✅ Token valide pour au moins 5 minutes")
       # Faire des opérations longues
   else:
       print("⚠️ Token expire dans moins de 5 minutes")
       client.authenticate("username", "password")

Exemple 3 : Workflow avec réauthentification manuelle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def faire_operation_critique(client):
       """Opération qui nécessite un token valide"""
       # Vérifier avant chaque opération critique
       if not client.is_token_valid(margin_seconds=120):
           print("⚠️ Token bientôt expiré, réauthentification...")
           client.authenticate("username", "password")

       # Faire l'opération
       return client.initiate_payment(...)

   with ArzekaPayment() as client:
       client.authenticate("username", "password")

       # Ces opérations vérifieront le token
       result1 = faire_operation_critique(client)
       time.sleep(3600)  # Attendre 1 heure
       result2 = faire_operation_critique(client)  # Se réauthentifiera

Exemple 4 : Boucle de monitoring
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import time
   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment()
   client.authenticate("username", "password")

   print("✅ Monitoring démarré")

   while True:
       if not client.is_token_valid():
           print("🔄 Token expiré, réauthentification...")
           client.authenticate("username", "password")

       # Effectuer des vérifications
       for order_id in get_pending_orders():
           status = client.check_payment(order_id)
           process_status(status)

       time.sleep(60)  # Vérifier toutes les minutes

Cas d'usage
-----------

✅ **Utilisez ``is_token_valid()`` quand :**

* Vous voulez juste savoir si le token est valide
* Vous devez prendre une décision binaire (continuer ou réauthentifier)
* Vous voulez un code simple et lisible
* Vous gérez manuellement la réauthentification

❌ **N'utilisez pas ``is_token_valid()`` si :**

* Vous utilisez déjà la réauthentification automatique (c'est fait automatiquement)
* Vous avez besoin d'informations détaillées sur l'expiration

Méthode ``get_token_expiry_info()``
====================================

Cette méthode retourne des informations détaillées sur l'expiration du token.

Signature
---------

.. code-block:: python

   def get_token_expiry_info(self) -> Dict[str, Any]

Valeur de retour
----------------

Un dictionnaire contenant :

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Champ
     - Type
     - Description
   * - ``is_valid``
     - ``bool``
     - ``True`` si le token est valide
   * - ``expires_at``
     - ``float`` ou ``None``
     - Timestamp Unix d'expiration (ou ``None`` si pas de token)
   * - ``expires_at_formatted``
     - ``str`` ou ``None``
     - Date d'expiration formatée (ISO 8601)
   * - ``seconds_remaining``
     - ``float`` ou ``None``
     - Secondes restantes avant expiration
   * - ``minutes_remaining``
     - ``float`` ou ``None``
     - Minutes restantes avant expiration
   * - ``hours_remaining``
     - ``float`` ou ``None``
     - Heures restantes avant expiration

Exemple de réponse
------------------

.. code-block:: python

   {
       "is_valid": True,
       "expires_at": 1709564421.0,
       "expires_at_formatted": "2026-02-23T15:47:01",
       "seconds_remaining": 2847.3,
       "minutes_remaining": 47.5,
       "hours_remaining": 0.79
   }

Exemples d'utilisation
-----------------------

Exemple 1 : Afficher les informations d'expiration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment()
   client.authenticate("username", "password")

   # Obtenir les informations détaillées
   info = client.get_token_expiry_info()

   print(f"Token valide : {info['is_valid']}")
   print(f"Expire le : {info['expires_at_formatted']}")
   print(f"Temps restant : {info['minutes_remaining']:.1f} minutes")

Exemple 2 : Décision basée sur le temps restant
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   info = client.get_token_expiry_info()

   if not info['is_valid']:
       print("❌ Token expiré")
       client.authenticate("username", "password")
   elif info['minutes_remaining'] < 5:
       print(f"⚠️ Token expire dans {info['minutes_remaining']:.1f} minutes")
       print("Réauthentification préventive...")
       client.authenticate("username", "password")
   else:
       print(f"✅ Token valide pour {info['hours_remaining']:.1f} heures")

Exemple 3 : Dashboard de monitoring
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def afficher_dashboard(client):
       """Afficher un dashboard de l'état du client"""
       info = client.get_token_expiry_info()

       print("=" * 50)
       print("  ARZEKA CLIENT STATUS")
       print("=" * 50)

       if info['is_valid']:
           print(f"Statut       : ✅ ACTIF")
           print(f"Expire à     : {info['expires_at_formatted']}")
           print(f"Temps restant: {info['hours_remaining']:.2f}h "
                 f"({info['minutes_remaining']:.0f}min)")
       else:
           print(f"Statut       : ❌ EXPIRÉ")
           print(f"Action       : Réauthentification requise")

       print("=" * 50)

   # Utilisation
   with ArzekaPayment() as client:
       client.authenticate("username", "password")
       afficher_dashboard(client)

Exemple 4 : Notification avant expiration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import time
   from fasoarzeka import ArzekaPayment

   def check_token_and_notify(client):
       """Vérifier le token et envoyer une notification si nécessaire"""
       info = client.get_token_expiry_info()

       if not info['is_valid']:
           send_alert("Token Arzeka expiré - Réauthentification requise")
           return False
       elif info['minutes_remaining'] < 10:
           send_warning(f"Token Arzeka expire dans {info['minutes_remaining']:.0f} minutes")
           return True
       return True

   client = ArzekaPayment()
   client.authenticate("username", "password")

   # Vérifier périodiquement
   while True:
       if not check_token_and_notify(client):
           client.authenticate("username", "password")
       time.sleep(300)  # Vérifier toutes les 5 minutes

Exemple 5 : Logging structuré
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import logging
   from fasoarzeka import ArzekaPayment

   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   client = ArzekaPayment()
   client.authenticate("username", "password")

   # Logger les informations du token
   info = client.get_token_expiry_info()

   logger.info("Token Information", extra={
       "is_valid": info['is_valid'],
       "expires_at": info['expires_at_formatted'],
       "minutes_remaining": info['minutes_remaining']
   })

Cas d'usage
-----------

✅ **Utilisez ``get_token_expiry_info()`` quand :**

* Vous avez besoin d'informations détaillées sur l'expiration
* Vous construisez un dashboard ou interface de monitoring
* Vous voulez logger des informations sur le token
* Vous devez prendre des décisions basées sur le temps restant

Comparaison des deux méthodes
==============================

Quand utiliser quelle méthode ?
--------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Besoin
     - ``is_token_valid()``
     - ``get_token_expiry_info()``
   * - Vérification simple
     - ✅ Oui
     - ❌ Trop complexe
   * - Informations détaillées
     - ❌ Non
     - ✅ Oui
   * - Dashboard/monitoring
     - ❌ Insuffisant
     - ✅ Parfait
   * - Performance
     - ✅ Très rapide
     - ✅ Rapide aussi
   * - Décision binaire
     - ✅ Idéal
     - ⚠️ Possible mais overkill
   * - Logging
     - ⚠️ Basique
     - ✅ Détaillé

Exemple comparatif
------------------

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment()
   client.authenticate("username", "password")

   # Approche 1 : Simple avec is_token_valid()
   if client.is_token_valid():
       print("✅ Token OK")
   else:
       print("❌ Token expiré")

   # Approche 2 : Détaillée avec get_token_expiry_info()
   info = client.get_token_expiry_info()
   if info['is_valid']:
       print(f"✅ Token OK (expire dans {info['minutes_remaining']:.1f} min)")
   else:
       print("❌ Token expiré")

Intégration avec la réauthentification automatique
===================================================

.. note::
   Si vous utilisez la réauthentification automatique, vous n'avez généralement
   **pas besoin** d'appeler ces méthodes manuellement. Le client gère tout automatiquement.

Cependant, ces méthodes restent utiles pour :

* **Monitoring** : Surveiller l'état du token
* **Logging** : Logger les informations d'authentification
* **Dashboard** : Afficher l'état en temps réel
* **Debugging** : Comprendre les problèmes d'authentification

Exemple avec réauth automatique
--------------------------------

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment()
   client.authenticate("username", "password")

   # Afficher l'état initial
   info = client.get_token_expiry_info()
   print(f"✅ Token valide pour {info['hours_remaining']:.1f}h")

   # Faire des opérations sans se soucier du token
   # La réauthentification est automatique
   response1 = client.initiate_payment(...)
   response2 = client.check_payment(...)

   # Vérifier l'état après les opérations
   info = client.get_token_expiry_info()
   print(f"Statut après opérations : {info['is_valid']}")

Best practices
==============

1. **Utiliser une marge de sécurité appropriée**

   .. code-block:: python

      # Pour des opérations rapides
      if client.is_token_valid(margin_seconds=60):
          ...

      # Pour des opérations longues
      if client.is_token_valid(margin_seconds=300):
          ...

2. **Logger les informations d'expiration**

   .. code-block:: python

      import logging

      info = client.get_token_expiry_info()
      logger.info(f"Token expires in {info['minutes_remaining']:.1f} minutes")

3. **Combiner avec la réauthentification automatique**

   .. code-block:: python

      # Le meilleur des deux mondes
      client = ArzekaPayment()
      client.authenticate("username", "password")

      # Utiliser is_token_valid() pour logging/monitoring
      if not client.is_token_valid(margin_seconds=300):
          logger.warning("Token will expire soon")

      # Mais laisser la réauthentification automatique gérer le reste
      response = client.initiate_payment(...)  # Auto re-auth if needed

4. **Vérifications périodiques dans les applications long-running**

   .. code-block:: python

      import time

      while True:
           info = client.get_token_expiry_info()

           if info['minutes_remaining'] < 10:
               logger.warning(f"Token expires in {info['minutes_remaining']:.0f} min")

           # Faire le travail
           do_work()

           time.sleep(60)

Prochaines étapes
=================

* :doc:`auto_reauth` : Réauthentification automatique
* :doc:`authentication` : Guide complet de l'authentification
* :doc:`best_practices` : Bonnes pratiques
* :doc:`api_reference` : Référence complète de l'API
