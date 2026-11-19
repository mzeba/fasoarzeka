# Changelog

Toutes les modifications notables de ce projet sont documentées ici.
Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le projet
respecte le [versionnage sémantique](https://semver.org/lang/fr/).

Le détail est aussi disponible dans la
[documentation](https://fasoarzeka.readthedocs.io/fr/latest/changelog.html).

## [0.2.0] - non publiée

### Ajouté

- Traduction des messages d'erreur : `install_translations()` et catalogue français
  complet (31 messages). Les messages restent en anglais par défaut.
- Scripts `scripts/extract_messages.sh` et `scripts/compile_messages.sh`.
- Marqueur `py.typed` (PEP 561) : les type hints sont pris en compte par mypy et pyright.
- Exception `ArzekaAuthenticationAPIError`, à la fois `ArzekaAuthenticationError` et
  `ArzekaAPIError`, levée pour les erreurs HTTP de l'authentification (401, 403, 5xx).
- Export de `ArzekaAPIError` depuis le package.

### Corrigé

- Les requêtes POST ne sont plus jamais renvoyées automatiquement (seules les GET le
  sont) : rejouer `initiate_payment` pouvait créer deux fois le même paiement.
- La bibliothèque n'appelle plus `logging.basicConfig()` à l'import.
- Suppression de la contrainte `urllib3<1.27`, incompatible avec les paquets exigeant
  urllib3 2.x.
- Les paramètres sont validés avant le rafraîchissement du token (aucun appel réseau
  sur une donnée invalide).
- `__version__` ne lève plus d'exception quand le package n'est pas installé.
- URL de l'API corrigées dans la documentation.

### Modifié

- Python 3.10 ou supérieur requis. Sous Python 3.8 et 3.9, pip installe la 0.1.3.

### Retiré

- Client Orange Money ajouté par erreur dans ce dépôt (projet distinct).

## [0.1.3] - 2026-02-23

## [0.1.2] - 2026-01-25

## [0.1.1] - 2026-01-24

## [0.1.0] - 2026-01-24

## [0.0.1] - 2026-01-24

- Première publication sur PyPI.

[0.2.0]: https://github.com/mzeba/fasoarzeka/compare/0.1.3...HEAD
[0.1.3]: https://pypi.org/project/fasoarzeka/0.1.3/
[0.1.2]: https://pypi.org/project/fasoarzeka/0.1.2/
[0.1.1]: https://pypi.org/project/fasoarzeka/0.1.1/
[0.1.0]: https://pypi.org/project/fasoarzeka/0.1.0/
[0.0.1]: https://pypi.org/project/fasoarzeka/0.0.1/
