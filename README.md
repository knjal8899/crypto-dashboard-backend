# crypto-dashboard-backend
Crypto Dashboard Backend

Overview
- Django + Django REST Framework backend for crypto dashboard and chat assistant
- Auth (JWT), Coins data (CoinGecko), Rule‑based chat Q&A, Caching, Unit tests

Tech Stack
- Django 5, DRF, SimpleJWT
- Postgres, psycopg
- uv (dependency and env), ruff, black, pylint

Requirements
- Python 3.12 (uv pins it)
- Postgres running locally
- uv installed (pip install uv)

Setup
1) Install uv and pin Python
```bash
pip install uv
uv python pin 3.12
uv sync
```

2) Environment
Create `.env` (already scaffolded) and set values:
```dotenv
DJANGO_DEBUG=True
SECRET_KEY=dev-secret-change-me
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cointrackr
CORS_ALLOWED_ORIGINS=http://localhost:3000
ACCESS_TOKEN_LIFETIME_MIN=30
REFRESH_TOKEN_LIFETIME_DAYS=7
COINGECKO_API_BASE=https://api.coingecko.com/api/v3
COINGECKO_API_KEY=
COINGECKO_CACHE_TTL_SECONDS=300
```

3) Database
Create the database (example with psql):
```bash
psql -U postgres -c "CREATE DATABASE cointrackr;"
```

4) Migrations and superuser
```bash
uv run python src/manage.py migrate
$env:DJANGO_SUPERUSER_PASSWORD="Admin123!"; uv run python src/manage.py createsuperuser --noinput --username admin --email admin@example.com
```

Run
```bash
uv run python src/manage.py runserver 0.0.0.0:8000
```

Docker
- Build and run (reads .env for DATABASE_URL, etc.):
```bash
docker compose up --build
```
- Notes:
  - Use AWS RDS by setting `DATABASE_URL` in `.env` (e.g., `postgresql://USER:PASSWORD@HOST:5432/DBNAME`).
  - Container runs uv sync and serves via uvicorn ASGI.

Auth (JWT)
- Register: POST `/api/auth/register`
  - Body: { "username", "email", "password" }
- Login: POST `/api/auth/login`
  - Body: { "username", "password" } → returns `access`, `refresh`
- Me: GET `/api/auth/me` (Header: Authorization: Bearer <access>)
- Refresh: POST `/api/auth/refresh` (Body: { refresh })
- Logout: POST `/api/auth/logout` (Body: { refresh })

Coins API
- Top coins: GET `/api/coins/top?limit=10`
- History: GET `/api/coins/{coin_id}/history?days=30`

Chat Q&A (Rule‑based)
- Query: GET `/api/chat/query?text=...`
  - Examples:
    - text=What is the price of Bitcoin?
    - text=Show me the 7-day trend of Ethereum

Caching
- LocMem cache with TTL controlled by `COINGECKO_CACHE_TTL_SECONDS`
- Applied to CoinGecko calls (top coins, history, single coin market)

Testing
```bash
uv run python src/manage.py test accounts coins chat -v 2
```

Commit Convention
- Use: `feat | message` or `fix | message`

References
- Django REST Framework APIViews: https://www.django-rest-framework.org/api-guide/views/
- CoinGecko Coins API: https://docs.coingecko.com/v3.0.1/reference/coins-list