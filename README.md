# TV Status Command Center

Flask-based TV deployment dashboard with session login, role-based visibility, KPI cards, and a polished status table.

## Stack

- Python 3.11
- Flask
- SQLite
- Bootstrap 5 and Bootstrap Icons via CDN
- Custom CSS and JavaScript for theme switching, motion, and polished UI
- Gunicorn for deployment

## Default Credentials

- `admin@tvstatus.local` / `Admin@123`
- `ano.ops@tvstatus.local` / `Ano@123`
- `assembly.viewer@tvstatus.local` / `View@123`

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`

## Features

- Admin-only user creation and user role management
- Admin-only TV record creation and editing
- Role-scoped read-only access for non-admin users
- Persistent SQLite storage for users and TV records
- Dark theme and light theme toggle
- Search, status filtering, remarks, and audit-style updated metadata

## Deploy

This project can be deployed to:

- Render
- Railway
- Azure App Service
- Heroku-compatible platforms
- Any VPS with Gunicorn and a reverse proxy

Default process file:

```text
web: gunicorn app:app
```

## One-Click Style Render Setup

This repo now includes [render.yaml](C:/Users/urajp/OneDrive/Desktop/AIO/DASH/render.yaml) for a Render web service with:

- Python runtime
- `gunicorn app:app`
- generated `SECRET_KEY`
- persistent disk-backed SQLite at `/var/data/tv_status.db`

Render deployment flow:

1. Push this folder to a GitHub repo.
2. In Render, create a new Blueprint or Web Service from that repo.
3. Approve the settings from `render.yaml`.
4. Wait for the first deploy to finish.
5. Open the public `onrender.com` URL Render gives you.

Important:

- Use at least the `starter` plan if you want the persistent disk attached.
- The local `tv_status.db` is ignored via `.gitignore`; production data will live on Render's disk instead.

## Production Notes

- Change `SECRET_KEY` in `app.py`
- Move SQLite to a managed database if you need multi-instance hosting
- Replace seeded demo passwords with proper managed authentication
- Add HTTPS and environment-variable based secrets before public deployment
