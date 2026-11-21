# Changelog

Toutes les modifications notables de ce projet sont documentées ici.
Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le projet
respecte le [versionnage sémantique](https://semver.org/lang/fr/).

Le détail est aussi disponible dans la
[documentation](https://fasoarzeka.readthedocs.io/fr/latest/changelog.html).

## [0.2.0] - 2026-11-21

### Ajouté

- Traduction des messages d'erreur : `install_translations()` et catalogue français
  complet (31 messages). Les messages restent en anglais par défaut.
- Scripts `scripts/extract_messages.sh` et `scripts/compile_messages.sh`.
- Marqueur `py.typed` (PEP 561) : les type hints sont pris en compte par mypy et pyright.
- Exception `ArzekaAuthenticationAPIError`, à la fois `ArzekaAuthenticationError` et
  `ArzekaAPIError`, levée pour les erreurs HTTP de l'authentification (401, 403, 5xx).
- Export de `ArzekaAPIError` depuis le package.
- Constantes `PaymentStatus` (`COMPLETED`, `INCOMPLETE`, `PENDING`), `TEST_BASE_URL`
  et `PRODUCTION_BASE_URL`, conformes à la documentation officielle de la passerelle.
- `get_payment_request_id()` : lit la référence (`paymentRequestId`) au retour sur
  le site marchand.
- Ré-authentification automatique (une seule fois) quand la passerelle répond 403.
- `initiate_payment()` accepte les montants `Decimal`.

### Corrigé

- `check_payment()` encode les paramètres de l'URL : une référence contenant `&`,
  `+`, `#` ou un espace vérifiait une autre commande.
- `initiate_payment()` ne modifie plus le dict `additional_info` passé par l'appelant.
- Le montant minimum (100 FCFA) est désormais inclusif ; `bool`, NaN et l'infini
  sont refusés.
- Documentation alignée sur l'API officielle : `initiate_payment()` renvoie un tuple
  `(response, payment_data)` (les exemples faisant `response['url']` plantaient),
  champs `firstname`/`lastname` (et non `first_name`/`last_name`), vrais champs de
  réponse et vrais statuts ; suppression des fonctions, paramètres et champs
  inexistants (`generate_hash`, `generate_order_id`, `order_description`, `qrcode`,
  statuts `FAILED`/`CANCELLED`...).

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
- `get_reference()` génère un UUID4 (comme les exemples officiels) au lieu de
  `AAMMJJ.HHMMSS.microsecondes`, pour éviter les collisions entre serveurs.

## [0.1.3] - 2026-02-23

## [0.1.2] - 2026-01-25

## [0.1.1] - 2026-01-24

## [0.1.0] - 2026-01-24

## [0.0.1] - 2026-01-24

- Première publication sur PyPI.

[0.2.0]: https://github.com/mzeba/fasoarzeka/compare/0.1.3...0.2.0
[0.1.3]: https://pypi.org/project/fasoarzeka/0.1.3/
[0.1.2]: https://pypi.org/project/fasoarzeka/0.1.2/
[0.1.1]: https://pypi.org/project/fasoarzeka/0.1.1/
[0.1.0]: https://pypi.org/project/fasoarzeka/0.1.0/
[0.0.1]: https://pypi.org/project/fasoarzeka/0.0.1/
