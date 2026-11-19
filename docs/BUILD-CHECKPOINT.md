# Build checkpoint

## Status: B01, B02 and B03 complete (16 November 2026). Next: B04.

Base commit `1188df8`; `git status` was clean before work. No application code
changed: edits are documentation plus deployment environment pass-through in
`compose.yaml`. Nothing is committed; commits need explicit authorization.

## B01 - real baseline: COMPLETE

Environment inspected without printing secret values: macOS arm64, Python 3.14.2
in `backend/.venv` (fastapi 0.161.1, pydantic 2.14.1, psycopg 3.3.6 - match pins;
`pip check` clean), Node 24.21.0, npm 11.19.0, PostgreSQL 18.6 on localhost:5432,
`docker` absent (command not found).

| Command | Result |
|---|---|
| `cd backend && .venv/bin/python -m pytest` | **239 passed, 18 skipped**, 1 warning, 1.06s |
| same, with `SCHOLARCHECK_TEST_DATABASE_URL` on disposable `scholarcheck_test_b01` | **257 passed, 0 skipped**, 1 warning, 2.22s |
| `cd frontend && npm run test` | **76 passed** / 11 files, 1.64s |
| `npm run lint`; `npm run typecheck`; `npm run build` | all pass, no diagnostics; dist js 245.97 kB (gzip 75.53 kB) |

Skips are not passes: `test_launch.py` 4, `test_opportunity_storage.py` 3,
`test_publication_migration.py` 3, `test_publication_store.py` 8, every reason
"SCHOLARCHECK_TEST_DATABASE_URL is not set". Database created with
`psql -h localhost -d postgres -c 'CREATE DATABASE scholarcheck_test_b01'` and
dropped after the run; 0 leftover `scholarcheck_test_%` databases. The fixture
creates and drops an isolated schema per test. No provider or production
database was touched.

## B02 - no demonstrated release blocker: COMPLETE

No test, lint, typecheck or build step failed, so no release-critical code defect
is demonstrated; nothing was fixed and no work was invented. Status documents
reconciled with history preserved and labelled: README current status, ROADMAP
baseline section, S01 `EVIDENCE.md` (new 16 November section; the 5 November
section and the F-criterion ledger marked historical), and the BUILD-PLAN
next-work paragraph, whose "database integration outstanding" claim is now closed.

Open follow-up, not a blocker: FastAPI/Starlette httpx test-client deprecation
(test tooling only; not a `DeprecationWarning` subclass). The serializer warning
recorded earlier did not recur in three runs.

Changed files: `docs/BUILD-CHECKPOINT.md`, `README.md`, `docs/BUILD-PLAN.md`,
`docs/ROADMAP.md`, `docs/slices/S01/EVIDENCE.md`.

## B03 - deployment configuration prepared: COMPLETE (packaging checked, not built)

Read `Dockerfile`, `.dockerignore`, `compose.yaml`, `.env.example`,
`backend/app/config.py`, `backend/app/main.py`, `manage.py`, `api/limits.py`,
`api/opportunities.py`, `publication/pipeline.py`, `publication/model_pass.py`,
`monitoring/worker.py` and `docs/DEPLOYMENT.md`.

| Check | Finding |
|---|---|
| Packaging paths | Image copies `content` to `/srv/content` and app to `/srv/backend/app`; `manage.py` uses `parents[2]`, `publication/register.py` and `storage/opportunities.py` use `parents[3]`, which resolve to `/srv/content` in that layout and to the repo root locally. `schema.sql` ships as package data. Consistent - no change |
| Frontend in production | `npm run build` in a Node stage, `FRONTEND_DIST=/srv/frontend/dist`, mounted with `StaticFiles(html=True)` after the API routers; hash routing needs no SPA fallback. Verified live |
| PostgreSQL startup | Compose health check plus `depends_on: service_healthy` for both `web` and `monitor`; `python -m app.manage init` creates the schema explicitly. Consistent |
| Private audit storage | Named `audits` volume at `/srv/backend/var`, matching the pipeline's `var/audits` and the worker's `var/monitoring` defaults under `WORKDIR /srv/backend`; `.dockerignore` excludes `var`, so no local artifacts are baked in. Consistent |
| Non-root, proxy trust | `useradd scholarcheck`, `var` owned by it, Uvicorn `--no-proxy-headers`. Consistent with the documented rate-limit boundary |
| Report gate | 403 for a foreign `Origin`, 400 for the honeypot field, 503 without `REPORT_HASH_KEY`, 5 reports/hour then 429, 8 KiB body cap 413, only a 64-char HMAC stored and no address column. Verified live |
| Worker configuration | **Defect fixed:** `monitor` received model IDs but not `EXTRACT_COMMAND`/`CHECK_COMMAND`, so the documented command adapters could never run there; `web` received no model or adapter variables at all, so a live `docker compose run --rm web python -m app.publication.pipeline` could not configure any adapter. Both now pass `OPENAI_API_KEY`, `EXTRACT_MODEL`, `CHECK_MODEL`, `EXTRACT_COMMAND`, `CHECK_COMMAND` (empty values stay unconfigured) |

Native production rehearsal, 16 November 2026, disposable database
`scholarcheck_b03`, no provider or production database touched: `app.manage init`
then `publish-launch` published `cgsd-doctoral` revision 1 under policy
`s01.publication.3`; Uvicorn ran with `APP_ENV=production`, `FRONTEND_DIST` and
`--no-proxy-headers`; `scripts/smoke.py http://127.0.0.1:8017 --report` **passed**
(HTML root, health `environment=production`, catalogue/detail, empty search, RMIT
404, private keys absent, accepted report). Extra probes: `/api/docs` 200, static
root serves `#root`, `/content/...` 404, foreign origin 403, 9000-byte report 413,
sixth report 429, 5 rows with 64-char hashes and no address column. Server
stopped, database dropped, 0 `scholarcheck_b03` leftovers; the unrelated
`scholarcheck_test` database pre-dates this work (31 October) and was untouched.

`docs/DEPLOYMENT.md` now carries an input checklist (required vs optional, native
vs Compose, what the repository cannot supply), the TLS/proxy boundary, secret
injection rules, backups/restore expectations and resource-limit starting points.

**Not proven:** the Compose file parses as YAML and its env wiring was inspected,
but no image was built and no container was started - Docker is still absent. No
hosting target, domain, contact address or credential was created or invented.

Changed files: `compose.yaml`, `docs/DEPLOYMENT.md`, `docs/BUILD-CHECKPOINT.md`,
`docs/BUILD-PLAN.md`.

## B04 - adapter contract and hold path exercised; live model call blocked (PARTIAL)

No provider credential exists in this workspace: `OPENAI_API_KEY` is absent from
the shell and there is no `.env`. No live extraction or checking pass was run and
no model call was simulated. The credential-free half of B04 was done against the
real source page and the real code paths. Every artifact stayed in `var/b04/`
(gitignored): no tracked evidence file changed, and no database was touched
(`DATABASE_URL` was unset and `--publish` was not used, so nothing connected).

| Check | Finding |
|---|---|
| Fresh retention | `app.collect.snapshot.collect` fetched the registered CGRS D page through the robots and approved-host rules: 200, 24,287 characters, robots "no matching rule", retained under `var/b04/snapshots/`. The machine clock recorded `2026-11-19T11:14:55Z`; the published reading is `2026-11-02T14:32:25Z` |
| Source unchanged | The page text is identical to the published reading: same content-addressed id (`...dcfbf661`) and identical body sha256 `dcfbf661b0e9...`, so revision 1 still describes what the page says. Raw HTML shrank 55,734 → 55,703 bytes with a different raw hash: markup moved, wording did not, so the raw hash is not the change signal and the text hash is |
| Binding semantics | `Snapshot.fingerprint`, which a report records, hashes the whole reading including `retrieved_at`, so today's fingerprint `7c0f201a...` differs from the published `5b799c3d...` although the text matches. `content_hash` is the text hash and is what the worker compares for "unchanged". Both are confirmed on the two artifacts, so a matching text hash - not a matching report hash - is the evidence that the page did not change |
| Retention guard | Writing today's artifact back into `content/snapshots` raised `SnapshotExists(same_text=True)` and left the tracked file byte-identical (`3f276bae...`): a later fetch cannot overwrite the provenance a report was checked against |
| Adapter contract | With `EXTRACT_COMMAND`/`CHECK_COMMAND` set to a stub that logged its stdin and replayed recorded outputs (receipts in `var/b04/receipts/`), extraction received `{task: extract, snapshots: 1, schema: ExtractionProposal, previous_record: null}` and no candidate; checking received `{task: check, snapshots: 1, candidate: 24 facts, schema: list schema, no title}` and no previous record. Exit 0, and the audit directory held the nine expected artifacts |
| Rehearsal report | Decision `publish`, `assurance: source_checked`, content hash `92a21daf...` equal to the published `complete-run` report, 18 checks, checked_at `2026-11-19T11:15:24Z`. This is a rehearsal over recorded pass outputs, not a new model reading and not new evidence; it was not published and must not be cited as validation |
| Hold path | Replaying the same extraction with one verdict altered to `unsupported` produced decision `hold`, `assurance: insufficient_evidence` and two stated reasons: one naming the fact and saying the check returned unsupported, one naming the snapshot with no supported quote |
| Refusal guards | With no adapter configured the pipeline exits 1 with `Configure EXTRACT_COMMAND or its model and OPENAI_API_KEY` and creates no audit directory. A copy of the snapshot with `$40,000 per year` changed to `$30,000 per year` under the same id made extraction refuse: `component:cgsd-living-support.amount: the quoted span is not in the retained snapshot` |

`var/b04/negative-fixtures/` holds the altered snapshot and the altered verdict
file with a README saying they are not evidence; they exist only to show the
guards fire.

**Not proven:** the live provider call. Extraction and checking ran over recorded
outputs, so today's page has not been read by a model and the published report
keeps its `2026-11-03T18:40:32Z` check time. No tracked artifact received a new
check time.

Changed files: `README.md`, `docs/BUILD-CHECKPOINT.md`, `docs/ROADMAP.md`,
`docs/BUILD-PLAN.md`, `docs/slices/S01/EVIDENCE.md`.

## Unresolved blockers (priority order, all external)

1. Container build/start unexecuted: Docker is not installed in this workspace;
   packaging was reviewed statically and the native route rehearsed instead.
2. No deployed HTTPS origin, real contact address or deployed smoke check; the
   deploy checklist is written but every external input is still missing.
3. No live model-provider call: no `OPENAI_API_KEY` exists in this workspace. The
   command-adapter contract, the hold path and the refusal guards are exercised
   (B04), so what remains outstanding is the provider call itself.
4. Scheduled monitoring not exercised on a deployed target, and no backup or
   restore has been run against a real deployment.

## Next smallest task

B04 stays open on its live half only: run real extraction and separate evidence
checking over the retained page with runtime credentials and model IDs supplied
outside this repository, then keep the raw and validated outputs, snapshot
bindings, report and publish/hold decision, without printing credentials or
inventing a check time.

The next step that needs no credentials is B05, which depends on B04: finalize
the initial catalogue through the gate and retain every regression fixture and
unresolved hold with its reason. Only `cgsd-doctoral` has a publication record so
far. The B03 deploy checklist stays current; nothing in it can be filled in from
inside this repository.
