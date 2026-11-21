# Guide d'installation - Faso Arzeka Payment

Guide complet en ligne : <https://fasoarzeka.readthedocs.io/fr/latest/installation.html>

## Prérequis

- Python **3.10 ou supérieur** (sous Python 3.8 / 3.9, pip installe la version 0.1.3)
- Des identifiants API Faso Arzeka : username, password, hash secret, merchant ID

## Installation

### Depuis PyPI (recommandé)

```bash
pip install fasoarzeka
```

Avec Poetry :

```bash
poetry add fasoarzeka
```

Dans le `requirements.txt` de votre projet :

```text
fasoarzeka>=0.2,<0.3
```

### Version en développement (GitHub)

```bash
pip install git+https://github.com/mzeba/fasoarzeka.git
```

### Pour contribuer

```bash
git clone https://github.com/mzeba/fasoarzeka.git
cd fasoarzeka
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -e ".[dev]"
python -m pytest
```

## Vérifier l'installation

```bash
python -c "import fasoarzeka; print(fasoarzeka.__version__)"
```

## Premier essai

```python
from fasoarzeka import ArzekaPayment

# Environnement de test par défaut : https://pgw-test.fasoarzeka.bf/
with ArzekaPayment() as client:
    client.authenticate("username", "password")
    response, sent = client.initiate_payment(
        amount=1000,
        merchant_id="MERCHANT_123",
        link_for_update_status="https://votre-site.example/webhook",
        link_back_to_calling_website="https://votre-site.example/retour",
        additional_info={"firstname": "Awa", "lastname": "Ouédraogo", "mobile": "70000000"},
        hash_secret="votre_hash_secret",
    )
```

En production, passez explicitement l'URL de production :

```python
from fasoarzeka import PRODUCTION_BASE_URL, ArzekaPayment

client = ArzekaPayment(base_url=PRODUCTION_BASE_URL)  # https://pgw.fasoarzeka.bf/
```

## Messages d'erreur en français

```python
from fasoarzeka import install_translations

install_translations("fr")
```

## Résolution des problèmes courants

### `ModuleNotFoundError: No module named 'fasoarzeka'`

Le package n'est pas installé dans l'environnement Python utilisé :

```bash
which python && python -m pip show fasoarzeka
python -m pip install fasoarzeka
```

Si vous utilisez un environnement virtuel, vérifiez qu'il est bien activé.

### `ERROR: ... requires a different Python`

La version 0.2.0 exige Python 3.10 ou supérieur. Mettez Python à jour ou installez
`fasoarzeka==0.1.3`.

### Conflit de version `urllib3`

La version 0.1.3 imposait `urllib3<1.27`. Passez à la 0.2.0, qui ne contraint plus
urllib3 :

```bash
python -m pip install --upgrade fasoarzeka
```

## Liens

- Documentation : <https://fasoarzeka.readthedocs.io/fr/latest/>
- Changelog : [CHANGELOG.md](https://github.com/mzeba/fasoarzeka/blob/main/CHANGELOG.md)
- Signaler un problème : <https://github.com/mzeba/fasoarzeka/issues>
