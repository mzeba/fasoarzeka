==============================
Réauthentification automatique
==============================

Vue d'ensemble
==============

La réauthentification automatique est une fonctionnalité qui garantit que vos requêtes ne échouent jamais à cause d'un token expiré.
Le client vérifie automatiquement la validité du token avant chaque requête et se réauthentifie si nécessaire.

✅ **Avantages**

* Pas besoin de vérifier manuellement la validité du token
* Aucune interruption de service due à l'expiration du token
* Code plus simple et plus lisible
* Idéal pour les applications long-running

Fonctionnement
==============

Le processus de réauthentification automatique suit ces étapes :

1. **Stockage des credentials** : Lors de l'authentification initiale, le client stocke username et password
2. **Vérification automatique** : Avant chaque requête, le client vérifie si le token est valide
3. **Réauthentification** : Si le token est expiré, le client se réauthentifie automatiquement
4. **Exécution** : La requête est ensuite exécutée avec le nouveau token

.. note::
   Les credentials sont stockés uniquement en mémoire, jamais sur disque.

Comment ça marche
=================

Stockage des credentials
-------------------------

Lors de l'authentification, le client stocke automatiquement vos identifiants :

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment()
   client.authenticate("votre_username", "votre_password")

En coulisses, le client stocke :

* ``self._token`` : Le token d'accès JWT
* ``self._expires_at`` : Timestamp d'expiration du token
* ``self._username`` : Votre username (pour réauthentification)
* ``self._password`` : Votre password (pour réauthentification)

Vérification automatique avant chaque requête
----------------------------------------------

Avant ``initiate_payment()`` et ``check_payment()``, le client appelle automatiquement ``_ensure_valid_token()`` :

.. code-block:: python

   def _ensure_valid_token(self):
       """Vérifie la validité du token et réauthentifie si nécessaire"""
       if not self.is_token_valid():
           if not self._username or not self._password:
               raise ArzekaAuthenticationError(
                   "Token expired and no credentials stored for re-authentication"
               )
           # Réauthentification automatique
           self.authenticate(self._username, self._password)

Utilisation
===========

Avec instance de classe
------------------------

C'est la méthode recommandée pour bénéficier de la réauthentification automatique.

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   # Créer le client et s'authentifier
   client = ArzekaPayment()
   client.authenticate("votre_username", "votre_password")

   # Faire des requêtes sur une longue période
   # La réauthentification se fait automatiquement si nécessaire

   # Première requête (token valide)
   response1 = client.initiate_payment(
       amount=1000,
       merchant_id="MERCHANT_123",
       # ... autres paramètres
   )

   # ... le temps passe, le token expire ...

   # Deuxième requête (token expiré → réauthentification automatique)
   response2 = client.initiate_payment(
       amount=2000,
       merchant_id="MERCHANT_123",
       # ... autres paramètres
   )
   # ✅ Le client se réauthentifie automatiquement avant cette requête

   # Fermer le client
   client.close()

Avec Context Manager
--------------------

.. code-block:: python

   from fasoarzeka import ArzekaPayment
   import time

   with ArzekaPayment() as client:
       # S'authentifier une fois
       client.authenticate("username", "password")

       # Faire plusieurs opérations
       for i in range(10):
           response = client.initiate_payment(...)
           print(f"Paiement {i+1} initié")

           # Simuler un délai
           time.sleep(600)  # 10 minutes

           # La réauthentification se fait automatiquement si le token a expiré

Avec fonctions de convenance
-----------------------------

.. note::
   Les fonctions de convenance (``initiate_payment()``, ``check_payment()``) créent
   un nouveau client pour chaque appel, donc la réauthentification automatique n'est
   pas applicable dans ce cas.

Pour bénéficier de la réauthentification automatique, utilisez une instance de classe.

Exemples pratiques
==================

Exemple 1 : Application long-running
-------------------------------------

.. code-block:: python

   from fasoarzeka import ArzekaPayment
   import time

   # Application qui tourne en continu
   client = ArzekaPayment()
   client.authenticate("username", "password")

   print("✅ Application démarrée")

   try:
       while True:
           # Vérifier les paiements en attente
           pending_orders = get_pending_orders()

           for order in pending_orders:
               # La réauthentification se fait automatiquement si nécessaire
               status = client.check_payment(order['id'])

               if status['status'] == 'COMPLETED':
                   mark_as_paid(order['id'])
                   print(f"✅ Paiement {order['id']} confirmé")

           # Attendre avant la prochaine vérification
           time.sleep(300)  # 5 minutes

   except KeyboardInterrupt:
       print("Arrêt de l'application")
   finally:
       client.close()

Exemple 2 : API REST avec Flask
--------------------------------

.. code-block:: python

   from flask import Flask, request, jsonify
   from fasoarzeka import ArzekaPayment

   app = Flask(__name__)

   # Créer un client global (réutilisé pour toutes les requêtes)
   client = ArzekaPayment()

   @app.before_first_request
   def init_client():
       """Initialiser le client au démarrage de l'application"""
       client.authenticate("username", "password")
       print("✅ Client Arzeka initialisé")

   @app.route('/api/payment/initiate', methods=['POST'])
   def initiate_payment_endpoint():
       data = request.json

       try:
           # Le client se réauthentifie automatiquement si nécessaire
           response = client.initiate_payment(
               amount=data['amount'],
               merchant_id=data['merchant_id'],
               additional_info=data['additional_info'],
               mapped_order_id=data['order_id'],
               hash_secret=app.config['HASH_SECRET'],
               link_for_update_status=app.config['WEBHOOK_URL'],
               link_back_to_calling_website=app.config['RETURN_URL']
           )

           return jsonify(response), 200

       except Exception as e:
           return jsonify({'error': str(e)}), 500

   @app.route('/api/payment/status/<order_id>', methods=['GET'])
   def check_payment_endpoint(order_id):
       try:
           # Réauthentification automatique si nécessaire
           status = client.check_payment(order_id)
           return jsonify(status), 200
       except Exception as e:
           return jsonify({'error': str(e)}), 500

   if __name__ == '__main__':
       try:
           app.run(debug=True)
       finally:
           client.close()

Exemple 3 : Worker de traitement en arrière-plan
-------------------------------------------------

.. code-block:: python

   from fasoarzeka import ArzekaPayment
   import redis
   import json
   import time

   # Connexion Redis pour la queue
   redis_client = redis.Redis(host='localhost', port=6379, db=0)

   # Client Arzeka
   arzeka_client = ArzekaPayment()
   arzeka_client.authenticate("username", "password")

   print("✅ Worker démarré")

   while True:
       # Récupérer un paiement de la queue
       _, payment_data = redis_client.blpop('payment_queue')
       payment = json.loads(payment_data)

       try:
           # Initier le paiement (réauth auto si nécessaire)
           response = arzeka_client.initiate_payment(
               amount=payment['amount'],
               merchant_id=payment['merchant_id'],
               # ... autres paramètres
           )

           print(f"✅ Paiement {payment['order_id']} initié")

           # Stocker le résultat
           redis_client.set(
               f"payment:{payment['order_id']}",
               json.dumps(response)
           )

       except Exception as e:
           print(f"❌ Erreur : {e}")
           # Remettre dans la queue ou logger l'erreur

Comparaison avant/après
=======================

Sans réauthentification automatique (ancien code)
--------------------------------------------------

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment()
   client.authenticate("username", "password")

   # Avant chaque requête, vérifier manuellement
   if not client.is_token_valid():
       print("Token expiré, réauthentification...")
       client.authenticate("username", "password")

   response = client.initiate_payment(...)

   # ... plus tard ...

   # Encore vérifier manuellement
   if not client.is_token_valid():
       print("Token expiré, réauthentification...")
       client.authenticate("username", "password")

   status = client.check_payment(...)

   # ❌ Répétitif et facile d'oublier

Avec réauthentification automatique (nouveau code)
---------------------------------------------------

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment()
   client.authenticate("username", "password")

   # Pas besoin de vérifier, c'est automatique !
   response = client.initiate_payment(...)

   # ... plus tard ...

   # Toujours pas besoin de vérifier
   status = client.check_payment(...)

   # ✅ Simple et sans risque d'oubli

Gestion des erreurs
===================

Erreur : Pas de credentials stockés
------------------------------------

Si vous appelez ``initiate_payment()`` ou ``check_payment()`` sans vous être authentifié au préalable :

.. code-block:: python

   from fasoarzeka import ArzekaPayment, ArzekaAuthenticationError

   client = ArzekaPayment()

   # Pas d'authentification !

   try:
       response = client.initiate_payment(...)
   except ArzekaAuthenticationError as e:
       print(f"❌ Erreur : {e}")
       # → "Token expired and no credentials stored for re-authentication"

**Solution** : Toujours s'authentifier au moins une fois :

.. code-block:: python

   client = ArzekaPayment()
   client.authenticate("username", "password")  # ✅
   response = client.initiate_payment(...)

Erreur : Credentials invalides
-------------------------------

Si les credentials stockés deviennent invalides (changement de mot de passe) :

.. code-block:: python

   client = ArzekaPayment()
   client.authenticate("username", "old_password")

   # ... le mot de passe est changé sur le serveur ...

   try:
       response = client.initiate_payment(...)
   except ArzekaAuthenticationError as e:
       print(f"❌ Réauthentification échouée : {e}")
       # Mettre à jour les credentials
       client.authenticate("username", "new_password")

Considérations de sécurité
===========================

Stockage en mémoire uniquement
-------------------------------

Les credentials sont stockés **uniquement en mémoire** :

* ✅ **Sécurisé** : Pas de persistence sur disque
* ✅ **Temporaire** : Supprimés à la fin du programme
* ✅ **Isolé** : Chaque instance de client a ses propres credentials

.. warning::
   Même si le stockage est sécurisé, suivez ces bonnes pratiques :

   * Utilisez HTTPS en production
   * Ne loggez jamais les credentials
   * Utilisez des variables d'environnement
   * Limitez l'accès au serveur d'application

Variables d'environnement
--------------------------

La meilleure pratique est d'utiliser des variables d'environnement :

.. code-block:: python

   import os
   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment()
   client.authenticate(
       os.getenv('ARZEKA_USERNAME'),
       os.getenv('ARZEKA_PASSWORD')
   )

Rotation des credentials
-------------------------

Si vous devez changer régulièrement de credentials :

.. code-block:: python

   def rotate_credentials(client, new_username, new_password):
       """Mettre à jour les credentials du client"""
       try:
           client.authenticate(new_username, new_password)
           print("✅ Credentials mis à jour")
       except ArzekaAuthenticationError as e:
           print(f"❌ Échec de la mise à jour : {e}")
           raise

   # Utilisation
   client = ArzekaPayment()
   client.authenticate("old_username", "old_password")

   # ... après un certain temps ...

   rotate_credentials(client, "new_username", "new_password")

Performance
===========

La réauthentification automatique a un impact minimal sur les performances :

* ✅ **Vérification rapide** : ``is_token_valid()`` est très rapide (simple comparaison de timestamp)
* ✅ **Réauthentification rare** : Se produit seulement quand le token expire (toutes les heures typiquement)
* ✅ **Pas de surcharge** : Pas de requête supplémentaire si le token est valide

Benchmark
---------

.. code-block:: python

   import time
   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment()
   client.authenticate("username", "password")

   # Mesurer le temps de 100 vérifications
   start = time.time()
   for _ in range(100):
       client.is_token_valid()
   elapsed = time.time() - start

   print(f"100 vérifications en {elapsed:.4f}s")
   # Résultat typique : 0.0001s (quasi instantané)

Prochaines étapes
=================

* :doc:`token_validation` : Validation et vérification des tokens
* :doc:`best_practices` : Bonnes pratiques de sécurité
* :doc:`logging` : Configuration du logging
* :doc:`api_reference` : Référence complète de l'API
