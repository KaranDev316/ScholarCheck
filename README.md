# ScholarCheck

A scholarship decision tool: it tells an international applicant, with checkable
evidence, whether a funded research master's really fits their profile, what the
funding covers, which deadline applies, and what to do next.

Planning documents live in [`docs/`](docs); implementation follows slice **S01**
(`docs/slices/S01/PLAN.md`).

## Stack

| Layer | Choice |
|---|---|
| Frontend | React 19 + TypeScript (strict), Vite 8, Vitest + Testing Library |
| Backend | FastAPI, Python 3.12+ (this machine: 3.14) |
| Data | PostgreSQL (schema and loader arrive in S01 T04) |
| Deferred | AI, accounts, background workers (see `docs/CONTEXT.md` D-05/D-06) |

## Repository layout

```
docs/       CONTEXT.md PRP.md ROADMAP.md slices/S01/{VERIFICATION,PLAN,EVIDENCE}.md
backend/    app/{api,domain,models} tests/
frontend/   src/{pages,components,api,types} tests/
content/    opportunities/*.yaml (reviewed seed data, S01 T03)
```

## Run locally

Prerequisites: Node 20+, Python 3.12+, npm.

### Backend (port 8000)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload --port 8000
```

- Health: <http://127.0.0.1:8000/api/health>
- API docs: <http://127.0.0.1:8000/api/docs>

### Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies `/api` to `http://127.0.0.1:8000`, so start the backend
first. Set `VITE_API_BASE_URL` to call a different API origin.

Environment variables (never committed): `APP_ENV`, `CORS_ALLOWED_ORIGINS`,
`DATABASE_URL` for the backend; `VITE_API_BASE_URL` for the frontend.

## Checks

```bash
cd backend  && .venv/bin/python -m pytest
cd frontend && npm run test && npm run lint && npm run typecheck && npm run build
```

`npm run typecheck` runs `tsc -b` because the project uses TypeScript project
references (a bare `tsc --noEmit` would check no files).

## Current status

S01 Step 1 complete: repository scaffold, shared domain types, health endpoint,
and a home page that reports API connectivity. Nothing is committed and no
fixture content exists yet — seed data requires human verification against the
official sources (S01 T03).
