# 3DVista Admin Portal (MVP)

Admin portal for managing virtual-tour clients and their e-learning statistics.

- **Backend:** Django 6 + Django REST Framework + JWT (SQLite)
- **Frontend:** React + TypeScript + Vite + TailwindCSS

## Prerequisites
- Python 3.12+ (built/tested on 3.14)
- Node 18+ (built/tested on 24)

## Run the backend (http://localhost:8000)
```bash
cd backend
source venv/bin/activate            # venv already created; or: python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt     # only needed on a fresh venv
python manage.py migrate            # already applied; safe to re-run
python manage.py runserver 8000
```
Local-demo admin login: **admin / `Demo3DVista!2026`** (Django admin at http://localhost:8000/admin/).
> ⚠️ This credential is for the **local demo only**. In production the superuser
> is created from `DJANGO_SUPERUSER_*` env vars with a strong secret — never ship
> this password. See [Production / Security](#production--security).

## Run the frontend (http://localhost:5173)
```bash
cd frontend
npm install                         # only needed once
npm run dev
```
Open http://localhost:5173 and sign in with **admin / `Demo3DVista!2026`**.

> Both servers must be running. The frontend reads the API base URL from
> `frontend/.env` (`VITE_API_URL`, defaults to `http://localhost:8000/api`).

## API
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/api/auth/login/` | none | Get JWT `access` + `refresh` tokens |
| POST | `/api/auth/refresh/` | none | Refresh an access token |
| GET/POST | `/api/clients/` | JWT | List / create clients |
| GET/PUT/PATCH/DELETE | `/api/clients/:id/` | JWT | Retrieve / update / delete a client |
| GET/POST | `/api/clients/:id/results/` | JWT | List / create results for a client |
| POST | `/api/results/receive/` | **public** | Ingest a score payload from a 3DVista tour |

### Public ingest payload (from 3DVista JavaScript)
Identify the client by `client` (id) **or** `client_name`:
```json
{
  "client_name": "Acme Safety Tour",
  "employee_name": "Jane Doe",
  "score": 8,
  "total_score": 10,
  "answered_questions": 10,
  "total_questions": 10,
  "items_found": 4,
  "total_items": 5
}
```
```bash
curl -X POST http://localhost:8000/api/results/receive/ \
  -H "Content-Type: application/json" \
  -d '{"client_name":"Acme Safety Tour","employee_name":"Jane Doe","score":8,"total_score":10,"answered_questions":10,"total_questions":10,"items_found":4,"total_items":5}'
```

> The public ingest endpoint can be locked with a shared token: set `INGEST_TOKEN`
> on the backend and send it from the tour as the `X-Ingest-Token` header. Unset
> (default) it stays open for the local demo.

## Notes
- The JWT access token is held **in React memory only** — never in
  localStorage/sessionStorage. A full page reload logs the user out by design.
- Logout now also **revokes the refresh token server-side** (blacklist) via
  `POST /api/auth/logout/`.
- SQLite + the seeded data ship in `backend/db.sqlite3` (2 sample clients, results).

## Production / Security
The app runs the local demo with safe defaults and **hardens automatically when
`DJANGO_DEBUG=False`**. Configure production via environment variables (see
[`backend/.env.example`](backend/.env.example) and [`frontend/.env.example`](frontend/.env.example)):

```bash
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(64))')"
export DJANGO_ALLOWED_HOSTS="admin.example.com"
export CORS_ALLOWED_ORIGINS="https://admin.example.com"
export INGEST_TOKEN="$(python -c 'import secrets;print(secrets.token_urlsafe(48))')"
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_PASSWORD="<strong-secret>"
export DJANGO_SUPERUSER_EMAIL=admin@example.com
python manage.py migrate
python manage.py createsuperuser --noinput   # uses the env vars above
python manage.py check --deploy               # should report no issues
```

Security controls applied (mapped to the Cyber Neo report findings):
- **CN-001** Strong, env-injected superuser; the boot refuses insecure defaults when `DEBUG=False`.
- **CN-002/003** `DEBUG` and `SECRET_KEY` are env-driven; production requires a real secret.
- **CN-004** Public ingest is rate-limited, optionally token-gated (`X-Ingest-Token`), and returns non-enumerable errors.
- **CN-005** DRF throttling on login (`10/min`), API, and ingest.
- **CN-006** When `DEBUG=False`: HSTS, SSL redirect, secure/HttpOnly cookies, `nosniff`, `X-Frame-Options: DENY`; CSP + related headers on every response.
- **CN-008** Short-lived access tokens (60 min), refresh rotation + blacklist, server-side logout.
- **CN-009** Tour `<iframe>` is `sandbox`ed.
- **CN-010** Security logging of login success/failure, logout, and ingest accept/reject.
- **CN-007/011** `.gitignore` excludes `db.sqlite3`, `venv/`, and `.env`; secrets never live in `VITE_*` vars.
