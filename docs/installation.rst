============
Installation
============

Prérequis
=========

Compte API Arzeka
------------------

Pour utiliser cette bibliothèque, vous devez disposer d'un compte API Arzeka Money avec :

* **Username** : Votre identifiant d'authentification
* **Password** : Votre mot de passe d'authentification
* **Hash Secret** : Votre clé secrète pour la génération de hash
* **Merchant ID** : Votre identifiant marchand unique

.. note::
   Pour obtenir ces identifiants, contactez Faso Arzeka ou votre intégrateur.

Certificats SSL (optionnel)
----------------------------

En environnement de production, des certificats SSL peuvent être fournis par l'opérateur pour une sécurité renforcée.

Version Python
--------------

Cette bibliothèque nécessite **Python 3.8 ou supérieur**.

Vérifiez votre version de Python :

.. code-block:: bash

   python --version
   # ou
   python3 --version

Dépendances
===========

Les dépendances suivantes seront installées automatiquement :

* **requests** >= 2.31.0 : Pour les requêtes HTTP
* **setuptools** : Pour l'installation du package
* **urllib3** : Pour la gestion des connexions HTTP

Toutes les dépendances sont listées dans le fichier ``requirements.txt`` :

.. code-block:: text

   requests>=2.31.0
   setuptools
   urllib3

Installation
============

Installation avec pip (recommandé)
-----------------------------------

Depuis GitHub
^^^^^^^^^^^^^

.. code-block:: bash

   pip install git+https://github.com/mzeba/fasoarzeka.git

Depuis une branche spécifique
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pip install git+https://github.com/mzeba/fasoarzeka.git@nom-de-la-branche

Installation avec Poetry
-------------------------

Si vous utilisez Poetry pour la gestion des dépendances :

.. code-block:: bash

   poetry add git+https://github.com/mzeba/fasoarzeka.git

Installation en mode développement
-----------------------------------

Pour contribuer au projet ou modifier le code source :

.. code-block:: bash

   # Cloner le dépôt
   git clone https://github.com/mzeba/fasoarzeka.git
   cd fasoarzeka

   # Installer en mode éditable
   pip install -e .

   # Ou avec Poetry
   poetry install

Cette méthode crée un lien symbolique vers le code source, permettant de tester vos modifications en temps réel.

Installation des dépendances de développement
----------------------------------------------

Si vous souhaitez exécuter les tests ou contribuer au développement :

.. code-block:: bash

   # Installer les dépendances de développement
   pip install -r requirements-dev.txt

   # Ou avec Poetry
   poetry install --with dev

Vérification de l'installation
===============================

Pour vérifier que l'installation s'est bien déroulée :

.. code-block:: python

   import fasoarzeka
   print(fasoarzeka.__version__)
   # Affiche : 3.0.1

Ou testez l'import des principales classes :

.. code-block:: python

   from fasoarzeka import ArzekaPayment, authenticate, initiate_payment, check_payment
   print("✅ Installation réussie !")

Configuration
=============

Variables d'environnement (optionnel)
--------------------------------------

Vous pouvez configurer certains paramètres via des variables d'environnement :

.. code-block:: bash

   export ARZEKA_TOKEN="votre_token"
   export ARZEKA_MERCHANT_ID="votre_merchant_id"
   export ARZEKA_BASE_URL="https://pwg-test.fasoarzeka.com/"
   export ARZEKA_HASH_SECRET="votre_hash_secret"

Ces variables peuvent être utilisées dans votre code :

.. code-block:: python

   import os
   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment(
       token=os.getenv('ARZEKA_TOKEN'),
       base_url=os.getenv('ARZEKA_BASE_URL')
   )

Fichier de configuration (optionnel)
-------------------------------------

Vous pouvez également créer un fichier de configuration ``arzeka_config.py`` :

.. code-block:: python

   # arzeka_config.py
   ARZEKA_USERNAME = "votre_username"
   ARZEKA_PASSWORD = "votre_password"
   ARZEKA_MERCHANT_ID = "MERCHANT_123"
   ARZEKA_HASH_SECRET = "votre_secret"
   ARZEKA_BASE_URL = "https://pwg-test.fasoarzeka.com/"

.. warning::
   **Sécurité** : Ne commitez jamais vos identifiants dans un dépôt Git !
   Ajoutez ``arzeka_config.py`` dans votre ``.gitignore``.

Environnements de test et production
=====================================

URLs des environnements
-----------------------

* **Test** : ``https://pwg-test.fasoarzeka.com/``
* **Production** : ``https://pwg.fasoarzeka.com/``

.. tip::
   Commencez toujours par tester votre intégration en environnement de test avant de passer en production.

Exemple de configuration multi-environnements
----------------------------------------------

.. code-block:: python

   import os
   from fasoarzeka import ArzekaPayment

   # Déterminer l'environnement
   ENV = os.getenv('APP_ENV', 'test')

   # Configuration selon l'environnement
   if ENV == 'production':
       BASE_URL = "https://pwg.fasoarzeka.com/"
   else:
       BASE_URL = "https://pwg-test.fasoarzeka.com/"

   client = ArzekaPayment(base_url=BASE_URL)

Dépannage
=========

Problème : ImportError
-----------------------

Si vous rencontrez l'erreur ``ModuleNotFoundError: No module named 'fasoarzeka'`` :

1. Vérifiez que l'installation s'est bien terminée :

   .. code-block:: bash

      pip show fasoarzeka

2. Vérifiez que vous utilisez le bon environnement Python :

   .. code-block:: bash

      which python
      which pip

3. Réinstallez le package :

   .. code-block:: bash

      pip uninstall fasoarzeka
      pip install git+https://github.com/mzeba/fasoarzeka.git

Problème : SSL Certificate Error
---------------------------------

Si vous rencontrez des erreurs de certificat SSL :

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   # Désactiver la vérification SSL (déconseillé en production)
   client = ArzekaPayment(verify_ssl=False)

.. danger::
   Désactiver la vérification SSL expose vos données à des risques de sécurité.
   N'utilisez cette option qu'en environnement de test.

Problème : Connection Timeout
------------------------------

Si vos requêtes expirent fréquemment, augmentez le timeout :

.. code-block:: python

   from fasoarzeka import ArzekaPayment

   client = ArzekaPayment(timeout=30)  # 30 secondes

Prochaines étapes
=================

Maintenant que l'installation est terminée, consultez :

* :doc:`quickstart` : Guide de démarrage rapide avec exemples
* :doc:`authentication` : Comprendre l'authentification
* :doc:`api_reference` : Référence complète de l'API
