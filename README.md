# Suivi de commandes — Citerneo

Application web de gestion de clients et de commandes.  
Stack : **FastAPI** · **HTMX** · **Jinja2** · **SQLite** (PostgreSQL via Docker optionnel)

---

## Lancement rapide

**Prérequis :** Python 3.11+ et [uv](https://docs.astral.sh/uv/)

```bash
git clone <url-du-repo>
cd projet_test_citerneo
uv sync --system-certs
uv run uvicorn main:app --reload
```

Ouvrir `http://127.0.0.1:8000` — la base de données et les données de démo sont créées automatiquement.

**Identifiants par défaut :** `admin` / `admin`

---

## Configuration

Les variables d'environnement suivantes peuvent être définies avant le lancement :

| Variable | Défaut | Description |
|---|---|---|
| `APP_USERNAME` | `admin` | Nom d'utilisateur |
| `APP_PASSWORD` | `admin` | Mot de passe |
| `SECRET_KEY` | `dev-secret-...` | Clé de signature des sessions (à changer en prod) |

```bash
# Exemple
APP_USERNAME=dylan APP_PASSWORD=monmotdepasse SECRET_KEY=unerandomstring uv run uvicorn main:app
```

---

## Fonctionnalités

- **Clients** : création, liste, suppression, vue des commandes par client
- **Commandes** : création, liste, changement de statut en ligne
- **Filtres** : par client et par statut sur la liste des commandes
- **Export CSV** : export de la liste filtrée
- **Authentification** : login/logout avec session cookie signé

---

## Structure du projet

```
├── main.py                  # Point d'entrée : démarrage, init DB, seed, routes
├── pyproject.toml           # Dépendances (géré par uv)
├── app/
│   ├── auth.py              # Logique d'authentification (check credentials, require_auth)
│   ├── config.py            # Instance Jinja2 partagée
│   ├── database.py          # Connexion SQLite + activation des clés étrangères
│   ├── schemas.py           # Validation Pydantic des formulaires
│   ├── models/
│   │   ├── client.py        # Modèle Client
│   │   └── commande.py      # Modèle Order + enum OrderStatus
│   └── routes/
│       ├── auth.py          # GET/POST /login · GET /logout
│       ├── clients.py       # GET/POST/DELETE /clients/
│       └── commandes.py     # GET/POST /commandes/ · PATCH /commandes/{id}/statut · GET /commandes/export.csv
├── docker/
│   └── docker-compose.yml   # PostgreSQL (optionnel)
└── templates/
    ├── base.html            # Layout commun
    ├── auth/
    │   └── login.html
    ├── clients/
    │   ├── index.html       # Page principale clients
    │   ├── _list.html       # Fragment HTMX
    │   └── commandes.html   # Commandes d'un client
    └── commandes/
        ├── index.html       # Page principale commandes
        ├── _list.html       # Fragment HTMX
        └── _row.html        # Fragment HTMX (ligne statut)
```

---

## Base de données

```mermaid
erDiagram
    CLIENT ||--o{ COMMANDE : passe
    CLIENT {
        int id PK
        string name
        string email
        string phone
        string address
        datetime created_at
    }
    COMMANDE {
        int id PK
        string reference
        datetime created_at
        float total_amount
        string status
        int client_id FK
    }
```

Statuts possibles : `créée` → `confirmée` → `expédiée` → `livrée` · `annulée`

Suppression d'un client : ses commandes sont supprimées en cascade.

---

## Passer à PostgreSQL

```bash
# 1. Démarrer PostgreSQL via Docker
docker compose -f docker/docker-compose.yml up -d

# 2. Lancer l'app en pointant vers PostgreSQL
DATABASE_URL=postgresql://citerneo:citerneo@localhost:5432/citerneo uv run uvicorn main:app --reload
```

> **Note :** modifier `app/database.py` pour lire `DATABASE_URL` depuis l'environnement est nécessaire avant de faire tourner l'app avec PostgreSQL.

---

## Usage de l'IA

Ce projet a été développé avec l'assistance de **Claude (Anthropic)**.

L'IA a été utilisée pour : la structure initiale des fichiers, la génération des routes FastAPI et des templates HTMX/Jinja2, le débogage (import circulaire SQLModel, API Starlette, problème N+1).

Les choix d'architecture, la relecture du code, les ajustements de validation et les décisions techniques (cascade, clés étrangères SQLite, `secrets.compare_digest`) ont été faits et vérifiés manuellement.
