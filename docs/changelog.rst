=========
Changelog
=========

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Version 0.2.0 (non publiée)
===========================

Fonctionnalités ajoutées
-------------------------

* 🌍 **Traduction des messages d'erreur** : nouvelle fonction
  ``install_translations()`` et catalogue français complet (31 messages).
  Voir :doc:`i18n`. Les messages restent en anglais par défaut.
* 🛠️ Scripts ``scripts/extract_messages.sh`` et
  ``scripts/compile_messages.sh`` pour maintenir les traductions.

Corrections
-----------

* 🛡️ **Plus aucune requête POST n'est renvoyée automatiquement** : seules les
  lectures (GET) sont retentées. Rejouer ``initiate_payment`` après une erreur
  5xx ou un délai dépassé pouvait créer deux fois le même paiement.
* 🪵 La bibliothèque n'appelle plus ``logging.basicConfig()`` à l'import :
  la configuration des logs revient à l'application.
* 📦 Suppression de la contrainte ``urllib3<1.27``, qui rétrogradait urllib3
  et cassait les paquets exigeant urllib3 2.x.
* 🔐 Les erreurs HTTP de l'authentification lèvent
  ``ArzekaAuthenticationAPIError``, qui est à la fois une
  ``ArzekaAuthenticationError`` et une ``ArzekaAPIError`` (avec
  ``status_code``). Messages explicites pour les codes 401 et 403.
* ✅ Les paramètres sont validés **avant** le rafraîchissement du token :
  une donnée invalide n'entraîne plus d'appel réseau.
* ``ArzekaAPIError`` est désormais exportée par le package
  (``from fasoarzeka import ArzekaAPIError``), comme le montrait la doc.
* 📚 Correction des URL de l'API dans la documentation
  (``pgw-test.fasoarzeka.bf`` / ``pgw.fasoarzeka.bf``).

Modifications
-------------

* ⬆️ **Python 3.10 ou supérieur requis.** Sous Python 3.8 et 3.9, pip
  installe automatiquement la version 0.1.3.
* 🏷️ Ajout du marqueur ``py.typed`` : les type hints sont pris en compte par
  mypy et pyright.
* 🧹 Retrait du client Orange Money ajouté par erreur dans ce dépôt
  (projet distinct). Le package redevient identique à la 0.1.3 publiée,
  plus la traduction.

Version 3.0.1 (2026-02-23)
==========================

Fonctionnalités ajoutées
-------------------------

* ✨ **Réauthentification automatique** : Le client vérifie automatiquement la validité du token avant chaque requête et se réauthentifie si nécessaire
* ✨ **Validation des tokens** : Nouvelles méthodes ``is_token_valid()`` et ``get_token_expiry_info()`` pour vérifier la validité des tokens
* ✨ **Gestion améliorée des erreurs** : Hiérarchie d'exceptions personnalisées pour une meilleure gestion des erreurs
* ✨ **Retry automatique** : Retry automatique avec backoff exponentiel pour les erreurs temporaires
* ✨ **Logging intégré** : Système de logging complet pour tracer toutes les opérations
* ✨ **Type hints complets** : Support complet des type hints pour meilleure auto-complétion

Améliorations
-------------

* 🔧 Stockage des credentials pour réauthentification automatique
* 🔧 Calcul correct de ``_expires_at`` avec marge de sécurité
* 🔧 Session persistante pour meilleures performances
* 🔧 Context manager pour gestion automatique des ressources
* 🔧 Documentation complète au format Read the Docs

Corrections de bugs
-------------------

* 🐛 Correction du calcul de l'expiration du token
* 🐛 Amélioration de la gestion des erreurs réseau
* 🐛 Meilleure validation des paramètres

Documentation
-------------

* 📚 Documentation complète au format Sphinx/Read the Docs
* 📚 Guide de démarrage rapide
* 📚 Guide d'authentification détaillé
* 📚 Documentation de la réauthentification automatique
* 📚 Guide de gestion des erreurs
* 📚 Bonnes pratiques et recommandations

Tests
-----

* ✅ Tests unitaires complets
* ✅ Couverture de code >90%
* ✅ Tests d'intégration

Version 2.0.0
=============

Fonctionnalités
---------------

* Initiation de paiements
* Vérification du statut des paiements
* Support des webhooks
* Gestion basique des erreurs

Version 1.0.0
=============

Première version
----------------

* Client de base pour l'API Arzeka
* Authentification simple
* Initiation de paiements basique

.. note::
   Pour voir le changelog complet, consultez le fichier ``CHANGELOG.md`` à la racine du projet.
