=========
Changelog
=========

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

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
