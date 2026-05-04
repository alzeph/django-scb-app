# scb_auth

App Django réutilisable pour l'authentification par numéro de téléphone.

---

## Installation

1. Copiez le dossier `scb_auth/` dans votre projet Django.
2. Ajoutez-le à `INSTALLED_APPS` :

```python
INSTALLED_APPS = [
    ...
    "scb_auth",
]
```

3. Déclarez le modèle utilisateur personnalisé :

```python
AUTH_USER_MODEL = "scb_auth.User"
```

4. Lancez les migrations :

```bash
python manage.py migrate
```

---

## Configuration — `SCB_AUTH`

Toute la configuration passe par le dictionnaire `SCB_AUTH` dans `settings.py`.

| Clé               | Type         | Défaut  | Description                                                |
|-------------------|--------------|---------|------------------------------------------------------------|
| `OPTIONAL_FIELDS` | `list[str]`  | `[]`    | Champs à **désactiver**. Valeurs acceptées : voir ci-dessous |
| `OTP_LIFETIME`    | `int`        | `300`   | Durée de vie d'un OTP en secondes                          |
| `OTP_DIGITS`      | `int`        | `4`     | Nombre de chiffres du code OTP                             |
| `USE_OTP`         | `bool`       | `True`  | Active/désactive entièrement le modèle `OtpToken`          |

### Champs optionnels disponibles

| Nom du champ      | Ce qu'il apporte                                                  |
|-------------------|-------------------------------------------------------------------|
| `otp_secret`      | Secret TOTP sur le User + modèle `OtpToken` + méthodes OTP       |
| `status_verified` | Champ de statut + propriétés `is_verified` / `is_unauthorized`   |

---

## Exemples de configuration

### Garder tous les champs (comportement par défaut)

```python
# settings.py — aucune configuration nécessaire
# ou explicitement :
SCB_AUTH = {
    "OPTIONAL_FIELDS": [],
}
```

### Désactiver uniquement `status_verified`

```python
SCB_AUTH = {
    "OPTIONAL_FIELDS": ["status_verified"],
}
```

Le modèle `User` n'aura pas le champ `status_verified`, ni les propriétés
`is_verified` et `is_unauthorized`.

### Désactiver uniquement `otp_secret`

```python
SCB_AUTH = {
    "OPTIONAL_FIELDS": ["otp_secret"],
}
```

Le modèle `User` n'aura pas le champ `otp_secret` et `OtpToken` ne sera pas
créé en base de données.

### Désactiver les deux champs

```python
SCB_AUTH = {
    "OPTIONAL_FIELDS": ["otp_secret", "status_verified"],
}
```

### Personnaliser l'OTP

```python
SCB_AUTH = {
    "OPTIONAL_FIELDS": [],    # tout garder
    "OTP_DIGITS": 6,          # codes à 6 chiffres
    "OTP_LIFETIME": 120,      # 2 minutes
}
```

### Désactiver complètement l'OTP (sans retirer le champ du modèle)

```python
SCB_AUTH = {
    "USE_OTP": False,         # OtpToken ne sera pas créé
}
```

---

## Utilisation dans le code

### Récupérer un utilisateur

```python
from scb_auth.models import User

user = User.get("+2250700000000")   # lève DoesNotExist ou PermissionError
```

### Générer et vérifier un OTP

```python
from scb_auth.models import OtpToken

token, _ = OtpToken.objects.get_or_create(user=user)

code = token.generate_otp()          # renvoie le code en clair
is_valid = token.verify_otp(code)    # True / False
```

### Vérifier le statut (si status_verified activé)

```python
if user.is_verified:
    ...

if user.is_unauthorized:
    raise PermissionError("Compte non autorisé")
```

### Vérifier dynamiquement si un champ est présent

```python
from scb_auth.conf import is_field_enabled

if is_field_enabled("status_verified"):
    user.status_verified = User.StatusVerified.VERIFIED
    user.save()
```

---

## Structure des fichiers

```
scb_auth/
├── __init__.py
├── apps.py
├── conf.py          ← lecture de SCB_AUTH depuis settings
├── models.py        ← User, OtpSecretMixin, StatusVerifiedMixin, OtpToken
├── admin.py         ← administration Django (s'adapte aux champs actifs)
├── migrations/
│   └── __init__.py
└── README.md
```

---

## Notes importantes

- Après avoir modifié `OPTIONAL_FIELDS`, **regénérez les migrations** :
  ```bash
  python manage.py makemigrations scb_auth
  python manage.py migrate
  ```
- Ne modifiez pas `OPTIONAL_FIELDS` sur une base de données existante sans
  prévoir une migration de données.
- En mode `DEBUG=True`, `verify_otp()` retourne toujours `True`.