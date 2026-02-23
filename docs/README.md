# Documentation README

Ce dossier contient la documentation complète du projet au format Sphinx/Read the Docs.

## Structure

``` bash
docs/
├── conf.py                  # Configuration Sphinx
├── index.rst               # Page d'accueil
├── installation.rst        # Guide d'installation
├── quickstart.rst         # Guide de démarrage rapide
├── authentication.rst     # Documentation authentification
├── payments.rst           # Guide des paiements
├── auto_reauth.rst        # Réauthentification automatique
├── token_validation.rst   # Validation des tokens
├── api_reference.rst      # Référence API
├── exceptions.rst         # Documentation des exceptions
├── error_handling.rst     # Gestion des erreurs
├── best_practices.rst     # Bonnes pratiques
├── logging.rst            # Configuration du logging
├── utils.rst              # Utilitaires
├── changelog.rst          # Historique des versions
├── contributing.rst       # Guide de contribution
├── license.rst            # Licence
├── requirements.txt       # Dépendances pour build
└── Makefile              # Commandes de build

```

## Générer la documentation localement

### Prérequis

```bash
pip install -r requirements.txt
```

### Générer HTML

```bash
cd docs
make html
```

La documentation sera générée dans `docs/_build/html/`.

Ouvrez `docs/_build/html/index.html` dans votre navigateur.

### Générer PDF

```bash
cd docs
make latexpdf
```

### Live reload (développement)

```bash
cd docs
make livehtml
```

Ouvre un serveur local avec rechargement automatique.

### Nettoyer

```bash
cd docs
make clean
```

## Commandes disponibles

```bash
make html       # Générer HTML
make latexpdf   # Générer PDF
make epub       # Générer EPUB
make clean      # Nettoyer les builds
make livehtml   # Mode développement avec live reload
```

## Publier sur Read the Docs

1. Créez un compte sur <https://readthedocs.org/>
2. Importez le dépôt GitHub
3. Configurez le webhook (automatique)
4. La documentation sera automatiquement générée à chaque push

## Style de documentation

- Utilisez reStructuredText (.rst) pour les documents structurés
- Markdown (.md) est également supporté via myst-parser
- Suivez le style Read the Docs
- Utilisez des exemples de code pour illustrer
- Incluez des notes, avertissements avec les directives appropriées

## Exemples de directives

```rst
.. note::
   Ceci est une note importante

.. warning::
   Ceci est un avertissement

.. code-block:: python

   # Ceci est un exemple de code
   from fasoarzeka import ArzekaPayment
```

## Contribution

Pour contribuer à la documentation :

1. Ajoutez ou modifiez les fichiers .rst
2. Testez localement avec `make html`
3. Commitez et créez une Pull Request
4. La documentation sera automatiquement mise à jour

## Ressources

- [Documentation Sphinx](https://www.sphinx-doc.org/)
- [Read the Docs](https://docs.readthedocs.io/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Sphinx RTD Theme](https://sphinx-rtd-theme.readthedocs.io/)
