# AI ticketing system

Collects tasks from Gmail, Google Calendar and manual input, processes them with an AI layer,
and shows an ordered priority queue.

```
gmail / calendar / manual -> FastAPI -> AI processing -> Supabase Postgres -> React UI
```

This repo is an initial scaffold: configuration, wiring and module boundaries only.
Data models, ingestion logic and AI logic are intentionally empty.

## Layout

| Path                        | Purpose                                                          |
| --------------------------- | ---------------------------------------------------------------- |
| `frontend/`                 | Vite + React + Tailwind UI. Proxies `/api` to the backend.       |
| `backend/app/main.py`       | FastAPI entrypoint (CORS, router mounting).                      |
| `backend/app/core/`         | Settings (`config.py`) and Supabase JWT auth (`auth.py`).        |
| `backend/app/api/`          | HTTP routes. Currently `/api/health` and `/api/health/db`.       |
| `backend/app/integrations/` | Gmail and Google Calendar adapters + shared Google OAuth helper. |
| `backend/app/ingestion/`    | Empty. Will turn source data into tasks.                         |
| `backend/app/ai/`           | `TaskProcessor` interface, `AIPipeline` runner, no-op processor. |
| `backend/database/`         | Async SQLAlchemy engine/session and `Base`. `models/` is empty.  |
| `backend/tests/`            | pytest.                                                          |

## Setup

### 1. Environment

```bash
cp .env.example .env
```

Fill in `DATABASE_URL` (Supabase > Project Settings > Database, use the `postgresql+asyncpg://` prefix),
the Supabase keys, and Google OAuth credentials when you are ready for them.
`AUTH_ENABLED=false` skips JWT checks during early development.

### 2. Run with Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000 (docs at `/docs`)

### 3. Run without Docker

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# frontend (new terminal)
cd frontend
npm install
npm run dev
```

### 4. Tests

```bash
cd backend && pytest
```

## Google OAuth

Create an OAuth client in Google Cloud Console, enable the Gmail API and Google Calendar API, and add
`GOOGLE_REDIRECT_URI` as an authorized redirect URI. OAuth runs in the backend so refresh tokens
never reach the browser. Scopes live in `backend/app/integrations/google_auth.py`.

## Adding things later

- **Models:** add files under `backend/database/models/` that inherit `database.base.Base`, and import them in `models/__init__.py`. Add Alembic when you want migrations.
- **AI:** implement `TaskProcessor` in `backend/app/ai/processors/` and register it in `AIPipeline`.
- **New source:** subclass `SourceIntegration` in `backend/app/integrations/`.

## Tasks and Google sync

Tasks are either **specific day** (status 1, a `TASK_DISTRIBUTION` row with `week_start` + `day_of_week`) or
**week pool** (status 0, `TASK` row only). `deadline` is the chosen day, or the last day (Sunday) of the chosen week
for pool tasks. Weeks start on Monday in the frontend and the backend. Status 3 means done.

API (all under `/api`): `POST /task/add/{specific|pool}`, `GET /task/week?week_start=`, `GET /task/today?today=`,
`GET|PATCH /task/{id}`, `PATCH /task/{id}/done`, `DELETE /task/delete/{id}`.

### Create the new table

`GOOGLE_ACCOUNT` is new. `create_all` only adds missing tables, so run `python -m app.repositories.db_initialization`
from `backend/`. The `day_of_week` check constraint fix only applies to a freshly created `TASK_DISTRIBUTION` table.

### Google setup

1. In Google Cloud Console enable the **Google Calendar API** and the **Google Tasks API**.
2. Create an OAuth client (Web). Add `GOOGLE_REDIRECT_URI` as an authorized redirect URI.
3. Add these to `.env`:

```
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/integrations/google/callback
FRONTEND_URL=http://localhost:5173
# Webhooks only (Calendar push notifications need a public HTTPS URL, e.g. an ngrok tunnel to port 8000):
PUBLIC_BASE_URL=https://your-tunnel.example.com
GOOGLE_WEBHOOK_TOKEN=any-long-random-string
# Optional, signs the OAuth state. A random per-process value is used if empty:
OAUTH_STATE_SECRET=
```

4. Click **Connect Google** in the app. After consent the backend stores the tokens, imports your Google Tasks and
   creates the Calendar push channel. **Sync Google** re-imports on demand.

Google Tasks has no push notifications. Calendar notifications trigger a re-sync, but task edits made in Google only
arrive on the next sync (a periodic job is a good follow-up). Push channels expire; they are renewed on each sync.

### Backend tests

`pip install aiosqlite` to run the API tests against a temporary SQLite file; without it they are skipped.
