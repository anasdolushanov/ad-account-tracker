# Ad Account Tracker

A small full-stack app for tracking clients and the status of their ad accounts across platforms (Google Ads, Meta, OpenAI Ads, etc.).

**Stack:** Python (FastAPI + SQLAlchemy + SQLite) · React (Vite)

## Run it

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload        # http://localhost:8000/docs
pytest                               # run tests
```

**Frontend**
```bash
cd frontend
npm install
npm run dev                          # http://localhost:5173 (proxies /api to :8000)
```

## What works now
- Create / delete clients
- Add ad accounts per client with platform, status and notes
- Update status inline (not started → in progress → blocked → live)
- Summary counts by status
- API tests for the core flow

## Roadmap
- [ ] Per-account setup checklists (billing, pixel, domain verification, policy review)
- [ ] Activity log / status history per account
- [ ] Filtering and search across clients
- [ ] Auth and multi-user support (contractor vs. owner roles)
- [ ] Alembic migrations, Postgres option
- [ ] Docker Compose for one-command startup
- [ ] Reminders for accounts stuck in "blocked"
