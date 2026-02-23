============
Contribuer
============

Nous accueillons les contributions à ce projet ! Ce guide vous aidera à démarrer.

Comment contribuer
==================

1. Fork le projet
-----------------

Créez un fork du dépôt sur GitHub :

.. code-block:: bash

   # Via l'interface GitHub
   # Cliquez sur "Fork" en haut à droite

2. Cloner votre fork
--------------------

.. code-block:: bash

   git clone https://github.com/votre-username/fasoarzeka.git
   cd fasoarzeka

3. Créer une branche
--------------------

.. code-block:: bash

   git checkout -b feature/ma-nouvelle-fonctionnalite

Utilisez des noms de branches descriptifs :

* ``feature/nom`` : Nouvelle fonctionnalité
* ``fix/nom`` : Correction de bug
* ``docs/nom`` : Documentation
* ``refactor/nom`` : Refactoring

4. Faire vos modifications
---------------------------

Suivez les :ref:`directives-code` ci-dessous.

5. Tester vos modifications
----------------------------

.. code-block:: bash

   # Installer les dépendances de développement
   pip install -r requirements-dev.txt

   # Exécuter les tests
   pytest

   # Vérifier le coverage
   pytest --cov=fasoarzeka

   # Linter
   flake8 src/
   black src/
   mypy src/

6. Commiter vos changements
----------------------------

.. code-block:: bash

   git add .
   git commit -m "feat: ajouter nouvelle fonctionnalité"

Utilisez des messages de commit conventionnels :

* ``feat:`` : Nouvelle fonctionnalité
* ``fix:`` : Correction de bug
* ``docs:`` : Documentation
* ``style:`` : Formatting, pas de changement de code
* ``refactor:`` : Refactoring
* ``test:`` : Ajout de tests
* ``chore:`` : Maintenance

7. Pousser vers GitHub
-----------------------

.. code-block:: bash

   git push origin feature/ma-nouvelle-fonctionnalite

8. Créer une Pull Request
--------------------------

Allez sur GitHub et créez une Pull Request depuis votre branche.

.. _directives-code:

Directives de code
==================

Style de code
-------------

Nous suivons les conventions Python standard :

* **PEP 8** : Guide de style Python
* **PEP 484** : Type Hints
* **Black** : Formatage automatique

.. code-block:: python

   # ✅ BON
   def authenticate(username: str, password: str) -> Dict[str, Any]:
       """
       Authentifie l'utilisateur.

       Args:
           username: Nom d'utilisateur
           password: Mot de passe

       Returns:
           Dictionnaire d'authentification
       """
       # Code...

   # ❌ MAUVAIS
   def auth(u, p):
       # Code sans documentation ni types...

Docstrings
----------

Utilisez le format Google docstring :

.. code-block:: python

   def my_function(param1: str, param2: int) -> bool:
       """
       Description courte de la fonction.

       Description plus longue si nécessaire, expliquant
       le fonctionnement en détail.

       Args:
           param1: Description du paramètre 1
           param2: Description du paramètre 2

       Returns:
           Description de la valeur de retour

       Raises:
           ValueError: Quand param2 est négatif

       Example:
           >>> my_function("test", 42)
           True
       """
       if param2 < 0:
           raise ValueError("param2 must be positive")
       return True

Type hints
----------

Utilisez toujours les type hints :

.. code-block:: python

   from typing import Dict, List, Optional, Any

   def process_payment(
       amount: int,
       merchant_id: str,
       additional_info: Dict[str, str]
   ) -> Dict[str, Any]:
       ...

Tests
-----

Écrivez des tests pour toutes les nouvelles fonctionnalités :

.. code-block:: python

   import pytest
   from fasoarzeka import ArzekaPayment

   class TestArzekaPayment:
       def test_authenticate_success(self):
           """Test d'authentification réussie"""
           client = ArzekaPayment()
           auth = client.authenticate("user", "pass")

           assert 'access_token' in auth
           assert auth['token_type'] == 'Bearer'

       def test_authenticate_failure(self):
           """Test d'authentification échouée"""
           client = ArzekaPayment()

           with pytest.raises(ArzekaAuthenticationError):
               client.authenticate("wrong", "credentials")

Documentation
-------------

Documentez toutes les fonctions publiques :

.. code-block:: python

   def initiate_payment(self, amount: int, ...) -> Dict[str, Any]:
       """
       Initie un nouveau paiement.

       Cette méthode crée une transaction de paiement et retourne
       une URL vers laquelle rediriger l'utilisateur.

       Args:
           amount: Montant en FCFA (minimum 100)
           ...

       Returns:
           Dictionnaire contenant:
           - mappedOrderId: ID de la commande
           - url: URL de redirection
           - qrcode: QR code de paiement

       Raises:
           ArzekaValidationError: Si les données sont invalides
           ArzekaAPIError: Si l'API retourne une erreur

       Example:
           >>> response = client.initiate_payment(
           ...     amount=1000,
           ...     merchant_id="MERCHANT_123"
           ... )
       """

Domaines de contribution
========================

Code
----

* Nouvelles fonctionnalités
* Corrections de bugs
* Améliorations de performance
* Refactoring

Documentation
-------------

* Corrections de typos
* Amélioration des exemples
* Traductions
* Tutoriels

Tests
-----

* Nouveaux tests
* Amélioration de la couverture
* Tests d'intégration

Processus de review
===================

Les Pull Requests seront reviewées selon ces critères :

✅ **Code**

* [ ] Suit le style PEP 8
* [ ] Type hints inclus
* [ ] Docstrings présents
* [ ] Pas de code dupliqué

✅ **Tests**

* [ ] Tests unitaires ajoutés
* [ ] Tests passent
* [ ] Couverture maintenue/améliorée

✅ **Documentation**

* [ ] Documentation ajoutée/mise à jour
* [ ] Exemples inclus
* [ ] Changelog mis à jour

✅ **Commit**

* [ ] Messages de commit clairs
* [ ] Commits atomiques
* [ ] Branche à jour avec main

Ressources
==========

* **Code source** : https://github.com/mzeba/fasoarzeka
* **Issues** : https://github.com/mzeba/fasoarzeka/issues
* **Pull Requests** : https://github.com/mzeba/fasoarzeka/pulls
* **Documentation** : https://fasoarzeka.readthedocs.io

Questions ?
===========

Si vous avez des questions, n'hésitez pas à :

* Ouvrir une issue sur GitHub
* Contacter les mainteneurs

Merci de contribuer ! 🎉
