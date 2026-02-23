.. Faso Arzeka Payment documentation master file

Documentation Faso Arzeka Payment API
=======================================

.. only:: html

   .. image:: https://img.shields.io/badge/python-3.8+-blue.svg
      :target: https://www.python.org/downloads/
      :alt: Python 3.8+

   .. image:: https://img.shields.io/badge/License-MIT-yellow.svg
      :target: https://opensource.org/licenses/MIT
      :alt: License: MIT

Bienvenue sur la documentation du client Python pour l'API de paiement mobile **Faso Arzeka**
au Burkina Faso (version 3.0.1).

Client robuste et production-ready avec gestion automatique des erreurs, retry automatique,
et réauthentification automatique.

.. note::
   Cette bibliothèque est un client **non officiel** pour l'API Faso Arzeka.

Fonctionnalités principales
----------------------------

✅ **Authentification sécurisée** avec gestion automatique des tokens

✅ **Réauthentification automatique** quand le token expire

✅ **Gestion complète des erreurs** avec exceptions personnalisées

✅ **Retry automatique** avec backoff exponentiel

✅ **Logging intégré** pour traçabilité complète

✅ **Session persistante** pour meilleures performances

✅ **Type hints complets** pour meilleure auto-complétion

✅ **Context manager** pour gestion automatique des ressources

✅ **Validation des tokens** avec informations d'expiration

✅ **Tests unitaires complets** avec couverture >90%

Démarrage rapide
----------------

Installation
^^^^^^^^^^^^

.. code-block:: bash

   pip install git+https://github.com/mzeba/fasoarzeka.git

Exemple simple
^^^^^^^^^^^^^^

.. code-block:: python

   from fasoarzeka import authenticate, initiate_payment, check_payment

   # 1. Authentification
   auth = authenticate("votre_username", "votre_password")
   print(f"Token valide pendant {auth['expires_in']} secondes")

   # 2. Initialiser un paiement
   payment_data = {
       "amount": 1000,
       "merchant_id": "MERCHANT_123",
       "additional_info": {
           "first_name": "Jean",
           "last_name": "Dupont",
           "mobile": "22670123456"
       },
       "hash_secret": "votre_secret",
       "link_for_update_status": "https://exemple.com/webhook",
       "link_back_to_calling_website": "https://exemple.com/retour"
   }

   response = initiate_payment(payment_data)
   print(f"URL de paiement: {response['url']}")

   # 3. Vérifier le statut
   status = check_payment(payment_data['mapped_order_id'])
   print(f"Statut: {status['status']}")

Table des matières
------------------

.. toctree::
   :maxdepth: 2
   :caption: Guide de l'utilisateur

   installation
   quickstart
   authentication
   payments
   error_handling

.. toctree::
   :maxdepth: 2
   :caption: Fonctionnalités avancées

   auto_reauth
   token_validation
   logging
   best_practices

.. toctree::
   :maxdepth: 2
   :caption: Référence API

   api_reference
   exceptions
   utils

.. toctree::
   :maxdepth: 1
   :caption: Informations supplémentaires

   changelog
   contributing
   license

Index et recherche
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
