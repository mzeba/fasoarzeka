# FASO ARZEKA Mobile Money Payment API (Burkina Faso)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/mzeba/fasoarzeka/blob/main/LICENSE)

API client Python non officiel pour les paiements mobiles FASO ARZEKA au Burkina Faso.
Client robuste, production-ready avec gestion automatique des erreurs, retry automatique, et réauthentification automatique.

## ✨ Fonctionnalités principales

- ✅ **Authentification sécurisée** avec gestion automatique des tokens
- ✅ **Réauthentification automatique** quand le token expire
- ✅ **Gestion complète des erreurs** avec exceptions personnalisées
- ✅ **Retry automatique** avec backoff exponentiel (lectures GET uniquement : un paiement n'est jamais renvoyé automatiquement)
- ✅ **Logging intégré** pour traçabilité complète
- ✅ **Session persistante** pour meilleures performances
- ✅ **Type hints complets** pour meilleure auto-complétion
- ✅ **Context manager** pour gestion automatique des ressources
- ✅ **Validation des tokens** avec informations d'expiration
- ✅ **Messages d'erreur traduisibles** (français inclus)
- ✅ **Tests unitaires** (pytest)

## 📋 Prérequis

1. **Compte API Arzeka Money**
   - Username
   - Password
   - Hash Secret
   - Merchant ID

2. **Certificats SSL** (si fournis par l'opérateur)

3. **Python 3.10 ou supérieur**

## 📦 Dépendances

```txt
requests>=2.31.0
```

Le client nécessite Python 3.10 ou supérieur.

## 🚀 Installation

```bash
# Avec pip
pip install fasoarzeka

# Avec poetry
poetry add fasoarzeka

# Installation en mode développement
git clone https://github.com/mzeba/fasoarzeka.git
cd fasoarzeka
pip install -e ".[dev]"
```

## 🎯 Guide de démarrage rapide

### Option 1 : Utilisation avec fonctions de convenance (Recommandé)

```python
from fasoarzeka import authenticate, initiate_payment, check_payment

# 1. Authentifiez-vous une fois
auth = authenticate("your_username", "your_password")
print(f"Token expires in: {auth['expires_in']} seconds")

# 2. Initiez un paiement
payment_data = {
    "amount": 1000,  # Montant en FCFA (minimum 100)
    "merchant_id": "MERCHANT_123",
    "additional_info": {
        "firstname": "Jean",
        "lastname": "Dupont",
        "mobile": "22670123456"  # Numéro avec indicatif
    },
    "mapped_order_id": "T20220923.203221.24732",
    "hash_secret": "your_hash_secret",
    "link_for_update_status": "https://example.com/webhook",
    "link_back_to_calling_website": "https://example.com/return"
}

response, sent = initiate_payment(payment_data)
print(f"URL to redirect user for payment: {response['url']}")

# 3. Vérifiez le statut du paiement
payment_response = check_payment(sent['mappedOrderId'])
print(f"Payment status: {payment_response['status']}")
```

### Option 2 : Utilisation avec instance de classe

```python
from fasoarzeka import ArzekaPayment

# Utilisez le context manager pour gestion automatique
with ArzekaPayment() as client:
    # 1. Authentification
    auth = client.authenticate("your_username", "your_password")

    # 2. Vérifiez la validité du token
    if client.is_token_valid():
        print("Token is valid")

    # 3. Initiez un paiement
    response, payment_data = client.initiate_payment(
        amount=1000,
        merchant_id="MERCHANT_123",
        additional_info={
            "firstname": "Jean",
            "lastname": "Dupont",
            "mobile": "70123456"
        },
        mapped_order_id="T20220923.203221.24732",
        hash_secret="your_hash_secret",
        link_for_update_status="https://example.com/webhook",
        link_back_to_calling_website="https://example.com/return"
    )

    # 4. Vérifiez le statut
    status = client.check_payment("T20220923.203221.24732")

# Le client est automatiquement fermé
```

## 📚 Exemples détaillés

### Authentification et gestion des tokens

```python
from fasoarzeka import ArzekaPayment

client = ArzekaPayment()

# Authentification
auth = client.authenticate("username", "password")
print(f"Access Token: {auth['access_token']}")
print(f"Token Type: {auth['token_type']}")
print(f"Expires In: {auth['expires_in']} seconds")

# Vérifier la validité du token
if client.is_token_valid():
    print("Token is still valid")
else:
    print("Token has expired")

# Obtenir des informations détaillées sur le token
info = client.get_token_expiry_info()
print(f"Expires in {info['expires_in_minutes']:.1f} minutes")
print(f"Is expired: {info['is_expired']}")

client.close()
```

### Réauthentification automatique

```python
from fasoarzeka import ArzekaPayment

client = ArzekaPayment()
client.authenticate("username", "password")

# Faites plusieurs requêtes sur une longue période
# La réauthentification est AUTOMATIQUE si le token expire

for i in range(10):
    # Pas besoin de vérifier la validité du token !
    # Le client se réauthentifie automatiquement si nécessaire
    response, payment_data = client.initiate_payment(
        amount=1000,
        merchant_id="MERCHANT_123",
        additional_info={...},
        hash_secret="secret",
        link_for_update_status="https://...",
        link_back_to_calling_website="https://..."
    )
    print(f"Payment {i+1}: {payment_data['mappedOrderId']}")

client.close()
```

### Initialisation de paiement avec reçu

```python
from fasoarzeka import initiate_payment, authenticate

# Authentifiez-vous d'abord
authenticate("username", "password")

# Paiement avec génération de reçu
payment_data = {
    "amount": 5000,
    "merchant_id": "MERCHANT_123",
    "additional_info": {
        "firstname": "Marie",
        "lastname": "Kaboré",
        "mobile": "70987654",
        "generateReceipt": True,  # Activer la génération de reçu
        "paymentDescription": "Facture N°12345",
        "accountingOffice": "Bureau Principal",
        "accountantName": "Jean Traoré",
        "address": "Ouagadougou, Burkina Faso"
    },
    "hash_secret": "your_secret",
    "link_for_update_status": "https://example.com/webhook",
    "link_back_to_calling_website": "https://example.com/return",
    "mapped_order_id": "ORDER-2025-001"  # ID personnalisé
}

response, sent = initiate_payment(payment_data)
print(f"Payment URL: {response['url']}")
print(f"Order ID: {sent['mappedOrderId']}")
```

### Vérification de paiement

```python
from fasoarzeka import check_payment, authenticate

authenticate("username", "password")

# Vérification simple
status = check_payment("ORDER-2025-001")
print(f"Status: {status}")

# Vérification avec transaction ID
status = check_payment(
    mapped_order_id="ORDER-2025-001",
    transaction_id="TXN-12345"
)
print(f"Transaction Status: {status}")
```

### Utilisation des fonctions utilitaires

```python
from fasoarzeka import get_reference, format_msisdn, validate_phone_number

# Générer un ID de référence unique
ref = get_reference()
print(f"Reference: {ref}")  # Ex: REF-20251023-123456

# Formater un numéro de téléphone
msisdn = format_msisdn("70 12 34 56")
print(f"Formatted: {msisdn}")  # 22670123456

# Valider un numéro burkinabè
is_valid = validate_phone_number("70123456")
print(f"Valid: {is_valid}")  # True
```

## 🔒 Gestion des erreurs

Le client fournit des exceptions spécifiques pour différents types d'erreurs :

```python
from fasoarzeka import ArzekaPayment
from fasoarzeka.exceptions import (
    ArzekaPaymentError,
    ArzekaConnectionError,
    ArzekaValidationError,
    ArzekaAPIError,
    ArzekaAuthenticationError
)

client = ArzekaPayment()

try:
    # Tentative d'authentification
    client.authenticate("username", "password")

    # Tentative de paiement
    response, payment_data = client.initiate_payment(
        amount=1000,
        merchant_id="MERCHANT_123",
        additional_info={...},
        hash_secret="secret",
        link_for_update_status="https://...",
        link_back_to_calling_website="https://..."
    )

except ArzekaAuthenticationError as e:
    print(f"Authentication failed: {e}")

except ArzekaValidationError as e:
    print(f"Invalid data: {e}")

except ArzekaConnectionError as e:
    print(f"Connection error: {e}")

except ArzekaAPIError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response_data}")

except ArzekaPaymentError as e:
    print(f"General error: {e}")

finally:
    client.close()
```

## ⚙️ Configuration

### Variables d'environnement (recommandé)

```bash
# .env
ARZEKA_USERNAME=your_username
ARZEKA_PASSWORD=your_password
ARZEKA_MERCHANT_ID=MERCHANT_123
ARZEKA_HASH_SECRET=your_hash_secret
ARZEKA_BASE_URL=https://pgw-test.fasoarzeka.bf/
```

```python
import os
from fasoarzeka import ArzekaPayment

client = ArzekaPayment(
    base_url=os.getenv('ARZEKA_BASE_URL'),
    timeout=30
)

client.authenticate(
    os.getenv('ARZEKA_USERNAME'),
    os.getenv('ARZEKA_PASSWORD')
)
```

### Configuration du logging

```python
import logging
from fasoarzeka import ArzekaPayment

# Configurer le niveau de log
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

client = ArzekaPayment()
# Les logs détaillés seront affichés
```

### Messages d'erreur en français

Les messages d'erreur sont en anglais par défaut. Pour les afficher en français :

```python
from fasoarzeka import install_translations

install_translations("fr")  # ou install_translations() pour suivre LANG
```

Voir la [documentation i18n](https://fasoarzeka.readthedocs.io/fr/latest/i18n.html) pour contribuer une traduction.

## 🧪 Tests

Les tests se trouvent dans `tests/` :

```bash
# Installer le package avec les dépendances de développement
pip install -e ".[dev]"

# Exécuter tous les tests
python -m pytest

# Exécuter un fichier ou un test précis
python -m pytest tests/test_payment.py
python -m pytest tests/test_auth.py::TestAuthentication::test_authenticate_success

# Mesurer la couverture
python -m coverage run -m pytest && python -m coverage report
```

## 📖 Documentation complète

La documentation complète est en ligne : **https://fasoarzeka.readthedocs.io/fr/latest/**

- [Installation](https://fasoarzeka.readthedocs.io/fr/latest/installation.html)
- [Démarrage rapide](https://fasoarzeka.readthedocs.io/fr/latest/quickstart.html)
- [Authentification](https://fasoarzeka.readthedocs.io/fr/latest/authentication.html)
- [Paiements](https://fasoarzeka.readthedocs.io/fr/latest/payments.html)
- [Gestion des erreurs](https://fasoarzeka.readthedocs.io/fr/latest/error_handling.html)
- [Réauthentification automatique](https://fasoarzeka.readthedocs.io/fr/latest/auto_reauth.html)
- [Validation des tokens](https://fasoarzeka.readthedocs.io/fr/latest/token_validation.html)
- [Traduction des messages (i18n)](https://fasoarzeka.readthedocs.io/fr/latest/i18n.html)
- [Référence API](https://fasoarzeka.readthedocs.io/fr/latest/api_reference.html)

Pour la générer localement :

```bash
cd docs
pip install -r requirements.txt
make html
# Puis ouvrez _build/html/index.html dans votre navigateur
```

## 🏗️ Architecture

```text
fasoarzeka/
├── src/fasoarzeka/           # Package publié sur PyPI
│   ├── __init__.py           # Exports publics
│   ├── base.py               # BasePayment et ArzekaPayment (client)
│   ├── main.py               # Fonctions de convenance (client partagé)
│   ├── constants.py          # URL, endpoints, valeurs par défaut
│   ├── exceptions.py         # Exceptions personnalisées
│   ├── utils.py              # Fonctions utilitaires (référence, signature…)
│   ├── i18n.py               # Traduction des messages d'erreur
│   ├── locales/              # Catalogues de traduction (.po / .mo)
│   └── py.typed              # Marqueur PEP 561 (type hints)
├── tests/                    # Tests unitaires (pytest)
├── docs/                     # Documentation Sphinx (Read the Docs)
├── scripts/                  # Outils de traduction (extraction / compilation)
├── .github/workflows/        # CI : tests et publication PyPI
├── CHANGELOG.md
├── LICENSE
├── README.md
└── pyproject.toml            # Métadonnées et configuration de build
```

## 🔧 Classes et Exceptions

### Classes principales

- **`ArzekaPayment`** - Client principal pour interactions API
- **`BasePayment`** - Classe de base avec gestion session et requêtes

### Exceptions personnalisées

- **`ArzekaPaymentError`** - Exception de base
- **`ArzekaConnectionError`** - Erreurs de connexion réseau
- **`ArzekaValidationError`** - Erreurs de validation de données
- **`ArzekaAPIError`** - Erreurs retournées par l'API
- **`ArzekaAuthenticationError`** - Erreurs d'authentification

## 🚀 Fonctionnalités avancées

### 1. Retry automatique avec backoff exponentiel

```python
# Le client réessaie automatiquement en cas d'erreur réseau
# - Maximum 3 tentatives
# - Backoff exponentiel (1s, 2s, 4s)
# - Status codes: 429, 500, 502, 503, 504
from fasoarzeka import ArzekaPayment
client = ArzekaPayment()
# Les retries sont automatiques !
```

### 2. Session persistante avec connection pooling

```python
# Les connexions HTTP sont réutilisées pour meilleures performances
from fasoarzeka import ArzekaPayment
client = ArzekaPayment()
# La session est automatiquement gérée
```

### 3. Context manager

```python
# Gestion automatique des ressources
from fasoarzeka import ArzekaPayment
with ArzekaPayment() as client:
    client.authenticate("user", "pass")
    response, payment_data = client.initiate_payment(...)
# Fermeture automatique de la session
```

### 4. Instance partagée pour fonctions de convenance

```python
from fasoarzeka import authenticate, initiate_payment, get_shared_client, close_shared_client

# Les fonctions partagent une même instance
authenticate("user", "pass")
initiate_payment(payment_data)

# Accéder à l'instance partagée
client = get_shared_client()
print(client.is_token_valid())

# Nettoyer l'instance partagée
close_shared_client()
```

## 💡 Bonnes pratiques

### 1. Utiliser les variables d'environnement

```python
import os
from fasoarzeka import authenticate

username = os.getenv('ARZEKA_USERNAME')
password = os.getenv('ARZEKA_PASSWORD')
authenticate(username, password)
```

### 2. Utiliser le context manager

```python
from fasoarzeka import ArzekaPayment
with ArzekaPayment() as client:
    client.authenticate("user", "pass")
    # ... opérations ...
# Nettoyage automatique
```

### 3. Gérer les exceptions spécifiques

```python
try:
    response, payment_data = client.initiate_payment(...)
except ArzekaValidationError:
    # Données invalides
except ArzekaAuthenticationError:
    # Problème d'authentification
except ArzekaConnectionError:
    # Problème réseau
```

### 4. Vérifier les tokens avant longues opérations

```python
if client.is_token_valid(margin_seconds=300):  # 5 minutes
    # Token valide pour au moins 5 minutes
    long_operation()
```

### 5. Utiliser le logging pour debug

```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Logs détaillés des requêtes
```

## 🔍 API Reference

### ArzekaPayment

```python
class ArzekaPayment(base_url: str = BASE_URL, timeout: int = 30)
```

#### Méthodes

- **`authenticate(username, password)`** - Authentification et obtention du token
- **`initiate_payment(...)`** - Initialiser un paiement
- **`check_payment(mapped_order_id, transaction_id)`** - Vérifier statut paiement
- **`is_token_valid(margin_seconds=60)`** - Vérifier validité du token
- **`get_token_expiry_info()`** - Obtenir infos détaillées sur expiration
- **`close()`** - Fermer la session

### Fonctions utilitaires

- **`get_reference()`** - Générer ID de référence unique
- **`format_msisdn(phone)`** - Formater numéro de téléphone
- **`validate_phone_number(phone)`** - Valider numéro burkinabè

### Fonctions de convenance

- **`authenticate(username, password, base_url, timeout)`** - Authentification
- **`initiate_payment(payment_data, base_url, timeout)`** - Initialiser paiement
- **`check_payment(mapped_order_id, transaction_id, base_url, timeout)`** - Vérifier paiement
- **`get_shared_client()`** - Obtenir instance partagée
- **`close_shared_client()`** - Fermer instance partagée

## 📊 Statut du projet

- ✅ Authentification sécurisée
- ✅ Initialisation de paiements
- ✅ Vérification de statut
- ✅ Gestion complète des erreurs
- ✅ Retry automatique
- ✅ Réauthentification automatique
- ✅ Envoi et suivi de SMS
- ✅ Messages d'erreur traduisibles (français)
- ✅ Tests unitaires
- ✅ Documentation complète
- ✅ Type hints complets
- ✅ Logging intégré
- ✅ Publié sur PyPI

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. **Fork** le projet
2. **Créez** une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. **Committez** vos changements (`git commit -m 'Add some AmazingFeature'`)
4. **Pushez** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrez** une Pull Request

### Guidelines de contribution

- Suivre le style de code existant
- Ajouter des tests pour nouvelles fonctionnalités
- Mettre à jour la documentation
- S'assurer que tous les tests passent

## 📝 Changelog

Voir le [changelog](https://fasoarzeka.readthedocs.io/fr/latest/changelog.html) pour l'historique détaillé des modifications.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](https://github.com/mzeba/fasoarzeka/blob/main/LICENSE) pour plus de détails.

## 👥 Auteur

**Mohamed Zeba** - [m.zeba@mzeba.dev](mailto:m.zeba@mzeba.dev)

## 🙏 Remerciements

- L'équipe Arzeka pour l'API
- La communauté Python du Burkina Faso
- Tous les contributeurs

## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/mzeba/fasoarzeka/issues)
- **Email** : <m.zeba@mzeba.dev>
- **Documentation** : [GitHub Wiki](https://github.com/mzeba/fasoarzeka/wiki)

## ⚠️ Avertissement

Ceci est un client **non officiel** pour l'API Arzeka. Utilisez-le à vos propres risques.
Assurez-vous de respecter les conditions d'utilisation de l'API Arzeka.

## 🌟 Soutenez le projet

Si ce projet vous aide, n'oubliez pas de lui donner une ⭐ sur GitHub !

---

**Note importante** : Ce client utilise l'environnement de test par défaut.
Pour la production, assurez-vous de configurer l'URL de production :

```python
from fasoarzeka import PRODUCTION_BASE_URL, ArzekaPayment

client = ArzekaPayment(base_url=PRODUCTION_BASE_URL)  # https://pgw.fasoarzeka.bf/
```
