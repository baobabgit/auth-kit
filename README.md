# Auth Kit

Kit d’authentification HTTP **indépendant du métier**. Sessions Bearer, trois rôles (`administrator`, `analyste_nominatif`, `usager`), administration des comptes. SQLite ou PostgreSQL.

Dépôt : [https://github.com/baobabgit/auth-kit](https://github.com/baobabgit/auth-kit)

## Sous-module Git

Dans un autre projet :

```bash
git submodule add https://github.com/baobabgit/auth-kit.git vendor/auth-kit
git submodule update --init --recursive
export PYTHONPATH="$PYTHONPATH:vendor/auth-kit/src"
# ou : pip install -e vendor/auth-kit
```

Clone d’un hôte qui l’embarque déjà :

```bash
git clone --recurse-submodules <url-du-projet-hôte>
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

Rôles : `administrator`, `analyste_nominatif`, `usager`. Seul `administrator`
gère les comptes. On ne peut pas retirer le dernier administrateur actif.

## Tests

```bash
pip install -e ".[dev]"
python3 -m pytest -q
```

Couverture exigée : 100 % (branches comprises).
