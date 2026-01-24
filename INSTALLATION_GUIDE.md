# Guide d'Installation - Faso Arzeka Payment

## 📁 Structure correcte du projet

La librairie est maintenant organisée comme suit :

```bash
arzeka-payment/
├── src/
│   └── fasoarzeka/              # ← Package principal
│       ├── __init__.py          # ← Exports et métadonnées
│       ├── arzeka.py            # ← Classe principale ArzekaPayment
│       ├── exceptions.py        # ← Exceptions personnalisées
│       └── utils.py             # ← Fonctions utilitaires
├── test/
│   ├── __init__.py              # ← Tests package
│   └── test.py                  # ← Tests unitaires
├── docs/                        # ← Documentation
│   ├── QUICKSTART.md
│   ├── AUTHENTICATION.md
│   ├── AUTO_REAUTH.md
│   ├── TOKEN_VALIDATION.md
│   └── MODIFICATIONS_SUMMARY.md
├── examples/                    # ← Exemples d'utilisation
│   ├── authentication_example.py
│   ├── auto_reauth_example.py
│   ├── shared_client_example.py
│   ├── token_validation_example.py
│   ├── example.py
│   ├── test_auto_reauth.py
│   └── test_signature_improvements.py
├── CHANGELOG.md                 # ← Historique des modifications
├── INSTALLATION_GUIDE.md        # ← Ce fichier
├── LICENSE                      # ← Licence MIT
├── README.md                    # ← Documentation principale
├── requirements.txt             # ← Dépendances
├── setup.py                     # ← Configuration d'installation
├── setup.cfg                    # ← Configuration additionnelle
└── pyproject.toml               # ← Configuration Poetry
```

## 🚀 Installation

### Méthode 1 : Installation depuis GitHub (recommandée)

```bash
# Via pip depuis GitHub
pip install git+https://github.com/mzeba/fasoarzeka.git

# Ou en mode développement (pour contribuer)
git clone https://github.com/mzeba/fasoarzeka.git
cd fasoarzeka
pip install -e .
```

### Méthode 2 : Installation locale

Si vous avez téléchargé le code :

```bash
cd /chemin/vers/arzeka-payment
pip install -e .
```

**Note :** Le script `setup.py` configure automatiquement le chemin vers le répertoire `src/fasoarzeka/`

### Méthode 3 : Avec un environnement virtuel (recommandé)

```bash
# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Installer la librairie
pip install -e .

# Vérifier l'installation
pip list | grep fasoarzeka
```

## 📦 Utilisation

### Import de base

```python
# Import de la classe principale
from fasoarzeka import ArzekaPayment

# Import des fonctions utilitaires
from fasoarzeka import authenticate, initiate_payment, check_payment

# Import des exceptions
from fasoarzeka import (
    ArzekaAPIError,
    AuthenticationError,
    PaymentError,
    ValidationError
)
```

### Exemple d'utilisation simple

```python
from fasoarzeka import ArzekaPayment

# Créer une instance
client = ArzekaPayment()

# S'authentifier
try:
    auth_result = client.authenticate("votre_username", "votre_password")
    print("✅ Authentification réussie !")
except Exception as e:
    print(f"❌ Erreur d'authentification : {e}")

# Initier un paiement
try:
    payment_result = client.initiate_payment(
        amount=1000,
        phone_number="70123456",
        reference="REF123"
    )
    print("✅ Paiement initié !")
except Exception as e:
    print(f"❌ Erreur de paiement : {e}")
```

### Utilisation avec les fonctions utilitaires

```python
from fasoarzeka import authenticate, initiate_payment, check_payment

# Authentification
token = authenticate("username", "password")

# Initiation de paiement
result = initiate_payment(
    token=token,
    amount=500,
    phone_number="70123456"
)

# Vérification du statut
status = check_payment(token, result['reference'])
```

## 🔍 Vérification de l'installation

### Test rapide dans un terminal Python

```python
# Ouvrir Python
python

# Tester l'import
>>> import fasoarzeka
>>> print("✅ Import réussi !")
>>> print(f"Version : {fasoarzeka.__version__}")
>>> print("Modules disponibles :", dir(fasoarzeka))

# Tester la classe principale
>>> from fasoarzeka import ArzekaPayment
>>> client = ArzekaPayment()
>>> print("✅ Classe ArzekaPayment disponible !")
```

### Script de test complet

Créez un fichier `test_import.py` :

```python
#!/usr/bin/env python3
"""Test d'importation de fasoarzeka"""

def test_imports():
    try:
        # Test import principal
        import fasoarzeka
        print("✅ Import fasoarzeka : OK")

        # Test classe principale
        from fasoarzeka import ArzekaPayment
        print("✅ Import ArzekaPayment : OK")

        # Test fonctions utilitaires
        from fasoarzeka import authenticate, initiate_payment, check_payment
        print("✅ Import fonctions utilitaires : OK")

        # Test exceptions
        from fasoarzeka import ArzekaAPIError, AuthenticationError
        print("✅ Import exceptions : OK")

        # Test création d'instance
        client = ArzekaPayment()
        print("✅ Création d'instance ArzekaPayment : OK")

        print("\n🎉 Tous les tests d'importation ont réussi !")
        print(f"📦 Package installé : fasoarzeka v{fasoarzeka.__version__}")

    except ImportError as e:
        print(f"❌ Erreur d'importation : {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")

if __name__ == "__main__":
    test_imports()
```

Puis exécutez :

```bash
python test_import.py
```

## 🆘 Résolution des problèmes courants

### Problème : `ModuleNotFoundError: No module named 'fasoarzeka'`

**Solutions :**

1. **Vérifiez l'installation :**

   ```bash
   pip list | grep fasoarzeka
   ```

2. **Réinstallez :**

   ```bash
   pip uninstall fasoarzeka
   pip install -e .
   ```

3. **Vérifiez l'environnement Python :**

   ```bash
   which python
   which pip
   ```

4. **Avec un environnement virtuel :**

   ```bash
   source .venv/bin/activate  # Assurez-vous que le venv est activé
   pip install -e .
   ```

### Problème : `ImportError: attempted relative import with no known parent package`

**Solution :** Utilisez les imports absolus :

```python
# ✅ Correct
from fasoarzeka import ArzekaPayment

# ❌ Incorrect
from .arzeka import ArzekaPayment
```

### Problème : `AttributeError: module 'fasoarzeka' has no attribute 'ArzekaPayment'`

**Solution :** Vérifiez que `__init__.py` expose correctement les classes :

```python
# Dans fasoarzeka/__init__.py
from .arzeka import ArzekaPayment
from .exceptions import ArzekaAPIError
# etc.

__all__ = ['ArzekaPayment', 'ArzekaAPIError', ...]
```

## 📚 Exemples complets

Consultez le dossier `examples/` pour des exemples d'utilisation :

- `examples/authentication_example.py` - Exemples d'authentification
- `examples/example.py` - Exemple simple
- `examples/shared_client_example.py` - Client partagé
- `examples/auto_reauth_example.py` - Réauthentification automatique
- `examples/token_validation_example.py` - Validation des tokens
- `examples/test_auto_reauth.py` - Test réauthentification
- `examples/test_signature_improvements.py` - Test signatures améliorées

## 🔗 Installation dans un autre projet

Pour utiliser cette librairie dans un autre projet :

### 1. Depuis GitHub

```bash
# Dans votre nouveau projet
pip install git+https://github.com/mzeba/fasoarzeka.git
```

### 2. Ajout au requirements.txt

```text
# requirements.txt de votre projet
fasoarzeka @ git+https://github.com/mzeba/fasoarzeka.git
```

### 3. Utilisation

```python
# Dans votre nouveau projet
from fasoarzeka import ArzekaPayment

client = ArzekaPayment()
# ... utiliser la librairie
```

## ✅ Checklist finale

- [ ] La librairie est installée : `pip list | grep fasoarzeka`
- [ ] L'import fonctionne : `python -c "from fasoarzeka import ArzekaPayment"`
- [ ] La classe principale est accessible : `from fasoarzeka import ArzekaPayment`
- [ ] Un environnement virtuel est utilisé (recommandé)
- [ ] Les exemples fonctionnent
- [ ] La structure `src/fasoarzeka/` est en place

## 🎉 Félicitations

Votre librairie **fasoarzeka** est maintenant correctement installée et utilisable !

Pour plus d'aide, consultez :

- 📖 Documentation complète dans `docs/`
- 💡 Exemples dans `examples/`
- 🐛 Issues sur GitHub
- 📚 README.md pour l'utilisation générale

---
