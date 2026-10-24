# ScholarCheck

ScholarCheck's first release will be a public, no-account website with a small
set of the best-evidenced scholarships. Visitors will browse and search,
filter by country, study level and funding type, inspect stated eligibility,
deadlines and exact official evidence, open official application links, and
share scholarship pages. A worker will then monitor one published scholarship
and safely update or hold changes. Automatic discovery follows proven
monitoring. The four current fixtures remain regression inputs, not a launch
quota.

The [architecture](docs/ARCHITECTURE.md),
[publication policy](docs/PUBLICATION-POLICY.md), [roadmap](docs/ROADMAP.md)
and [S01 plan](docs/slices/S01/PLAN.md) describe the revised direction.

## Stack

| Layer | Choice |
|---|---|
| Frontend | React 19 + TypeScript (strict), Vite 8, Vitest + Testing Library |
| Backend | FastAPI, Python 3.12+ (this machine: 3.14) |
| Data | PostgreSQL with a repeatable fixture loader (S01 T04) |
| Planned pipeline | Source snapshots and validation for initial publication; then one-source scheduled monitoring |
| Deferred | Automatic discovery, personal assessments, saved items and accounts |

## Repository layout

```
docs/       ARCHITECTURE.md CONTEXT.md PRP.md ROADMAP.md PUBLICATION-POLICY.md slices/S01/
backend/    app/{api,domain,models} tests/
frontend/   src/{pages} tests/
content/    opportunities/*.yaml (unverified regression fixtures, S01 T03)
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

### Load development fixtures

Start a local PostgreSQL server and create a disposable development database,
then run:

```bash
cd backend
export DATABASE_URL='postgresql://localhost/scholarcheck'
.venv/bin/python -m app.storage.load_seeds
```

The loader is repeatable and refuses to overwrite a source-checked record.
Fixtures remain unpublished: `GET /api/v1/opportunities/{id}` shows them
with `insufficient_evidence` assurance in development/test only. Production
returns 404 until a future publication gate has approved a revision.

### Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies `/api` to `http://127.0.0.1:8000` for future public
catalogue calls. The current landing page does not call the API.

Environment variables (never committed): `APP_ENV`, `CORS_ALLOWED_ORIGINS`,
`DATABASE_URL` for the backend.

## Checks

```bash
cd backend  && .venv/bin/python -m pytest
cd frontend && npm run test && npm run lint && npm run typecheck && npm run build
```

PostgreSQL integration tests require a disposable database:
`SCHOLARCHECK_TEST_DATABASE_URL=postgresql://localhost/scholarcheck_test`.
They create and remove isolated schemas and skip when this variable is absent.

`npm run typecheck` runs `tsc -b` because the project uses TypeScript project
references (a bare `tsc --noEmit` would check no files).

## Current status

The scaffold, four regression fixtures, PostgreSQL loader and development read
endpoint exist. The public catalogue, publication gates, website journeys and
monitoring worker do **not** exist yet. The
[first-pass review](docs/slices/S01/FIRST-PASS-REVIEW.md) found material
route, rate-year and deadline issues, so the fixtures cannot yet be labelled
`source_checked` or published. The [roadmap](docs/ROADMAP.md) now finishes the
best-evidenced public MVP before monitoring one record and then adding
discovery. Legacy human-verification fields in code and fixtures still need
migration; they are no longer part of the product direction.
