# Auth Kit

Kit d’authentification HTTP **indépendant du métier**. Sessions Bearer, deux rôles (`administrator`, `usager`), administration des comptes. SQLite ou PostgreSQL.

## Sous-module Git

Ce répertoire est un paquet autonome. Dans un autre projet :

```bash
git submodule add <url-du-dépôt-auth-kit> vendor/auth-kit
git submodule update --init --recursive
export PYTHONPATH="$PYTHONPATH:vendor/auth-kit/src"
# ou : pip install -e vendor/auth-kit
```

Clone d’un hôte qui l’embarque déjà :

```bash
git clone --recurse-submodules <url-du-projet-hôte>
```

Pour publier ce dossier vers un dépôt vide :

```bash
cd vendor/auth-kit   # ou depuis une copie extraite
git init
git add .
git commit -m "Paquet auth-kit"
git remote add origin <url-du-dépôt-auth-kit>
git branch -M main
git push -u origin main
```

## Hôte FastAPI

```python
from auth_kit.auth_kit_application import AuthKitApplication
from auth_kit.auth_kit_settings import AuthKitSettings

settings = AuthKitSettings(
    database_url="postgresql://user:pass@localhost:5432/auth",
    bootstrap_identifier="admin",
    bootstrap_password="changeme",
)
app = AuthKitApplication(settings).create()
```

Factory uvicorn :

```bash
AUTH_DATABASE_PATH=data/auth.sqlite \
AUTH_BOOTSTRAP_IDENTIFIER=admin \
AUTH_BOOTSTRAP_PASSWORD=changeme \
PYTHONPATH=src uvicorn auth_kit.auth_kit_application:AuthKitApplication.create_default_app \
  --factory --host 127.0.0.1 --port 48103
```

Variables : `AUTH_DATABASE_URL` (prioritaire) ou `AUTH_DATABASE_PATH`, `AUTH_BOOTSTRAP_IDENTIFIER`, `AUTH_BOOTSTRAP_PASSWORD`.

Compte bootstrap uniquement si la base est vide. Défauts : identifiant `admin`, mot de passe `riftbound` (à surcharger).

## Client HTTP

```python
from auth_kit.auth_http_client import AuthHttpClient

auth = AuthHttpClient("http://127.0.0.1:48103")
session = auth.login("admin", "changeme")
user = auth.me(session.token)
```

Les autres services envoient `Authorization: Bearer <token>` et appellent `GET /me`.

| Méthode | Chemin | Accès |
| --- | --- | --- |
| `GET` | `/health` | public |
| `POST` | `/login` | `{identifier, password}` → `{token, user}` |
| `POST` | `/logout` | Bearer optionnel |
| `GET` | `/me` | Bearer |
| `GET` `/POST` | `/users` | administrateur |
| `PATCH` | `/users/{id}` | administrateur |

Rôles : `administrator`, `usager`. On ne peut pas retirer le dernier administrateur actif.

## Tests

```bash
pip install -e ".[dev]"
python3 -m pytest -q
```

Couverture exigée : 100 % (branches comprises).
