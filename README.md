# ScholarCheck

ScholarCheck's first release will be a public, no-account website with a small
set of the best-evidenced scholarships. Visitors will browse and search,
filter by country, study level and funding type, inspect stated eligibility,
deadlines and the actual check date, open official provider/application links, and
share scholarship pages. A worker will then monitor one published scholarship
and safely update or hold changes. Automatic discovery follows proven
monitoring. The four current fixtures remain regression inputs, not a launch
quota. Claim-linked evidence and retained snapshots stay in the backend.

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
backend/    app/{api,collect,domain,models,publication,storage} tests/
frontend/   src/{pages} tests/
content/    opportunities/*.yaml (unverified regression fixtures, S01 T03)
            snapshots/*.json (retained official-source pages a passage must match)
            publication/first-pass-review.json (findings that hold a fixture)
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
Fixtures remain unpublished. Every public opportunity endpoint reads only
published revisions, including in development. To publish the audited CGRS D
candidate in a configured database, run `.venv/bin/python -m app.manage
publish-launch` from `backend`. RMIT remains held. See [deployment and
monitoring instructions](docs/DEPLOYMENT.md).

### Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies `/api` to `http://127.0.0.1:8000`. Screens load the
published catalogue by default. Set `VITE_PREVIEW_DATA=true` only for explicitly
marked development previews. Production builds never use those fixtures.

Environment variables (never committed): `APP_ENV`, `CORS_ALLOWED_ORIGINS`,
`DATABASE_URL` for the backend.

## Checks

```bash
cd backend  && .venv/bin/python -m pytest
cd frontend && npm run test && npm run lint && npm run typecheck && npm run build
```

Retaining an official source page (checks `robots.txt` first, then keeps the
readable text and its provenance in `content/snapshots/`):

```bash
cd backend && PYTHONPATH=. .venv/bin/python -m app.collect.snapshot --out ../content/snapshots 'https://www.rmit.edu.au/scholarships/research/research-stipend'
```

PostgreSQL integration tests require a disposable database:
`SCHOLARCHECK_TEST_DATABASE_URL=postgresql://localhost/scholarcheck_test`.
They create and remove isolated schemas and skip when this variable is absent.

`npm run typecheck` runs `tsc -b` because the project uses TypeScript project
references (a bare `tsc --noEmit` would check no files).

## Current status

The validation pipeline, stricter publication gate, published-only catalogue
and detail APIs, connected website, protected problem reports and one-record
monitor are implemented. CGRS D has a retained proposal, separate evidence
adjudications and a passing report; real PostgreSQL tests cover publication,
unsupported-claim rejection and changed-source monitoring. RMIT remains held.
The public contract excludes evidence passages, snapshot IDs, policy and revision
metadata. Source-check dates and official links are public.

The production frontend build and local HTTP smoke test pass. A real hosting
origin, contact address and deployed smoke test remain outstanding. The built-in
model adapter needs runtime API credentials and explicit model IDs; its live
provider call has not been executed. See [release instructions](docs/DEPLOYMENT.md)
and the [evidence ledger](docs/slices/S01/EVIDENCE.md).
