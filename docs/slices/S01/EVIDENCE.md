# Evidence — S01 foundation

Status: **in progress under D-09**. The earlier “one complete decision”
acceptance criteria AC-01..AC-14 moved to S07. Current S01 criteria F-01..F-07
are in `VERIFICATION.md`. This file preserves completed scaffold and fixture
checks and records what remains unproven.

## Completed scaffold and fixture checks

| Check | Command recorded when run | Result |
|---|---|---|
| Backend scaffold suite | `cd backend && .venv/bin/python -m pytest` | 27 passed at Step 1 |
| Frontend tests | `cd frontend && npm run test` | 7 passed at Step 1 |
| Frontend typecheck, lint, build | `npm run typecheck`, `npm run lint`, `npm run build` | Passed at Step 1 |
| Seed content tests | `cd backend && .venv/bin/python -m pytest tests/test_seed_content.py` | 36 passed at T03 |
| Full backend suite | `cd backend && .venv/bin/python -m pytest` | 69 passed at T03 |

T03 created four YAML regression fixtures: CGRS D, UdeM doctoral exemption,
RMIT research stipend, and Sydney RTP stipend. Tests cover model parsing,
unique ids and evidence references, blocking-rule evidence, funding component
shape, separate retrieval/human timestamps, and intentionally unspecified
values. The 2026-10-23 content pass recorded 13/13 source URLs responding,
19 passages matching after whitespace normalisation, and six table
transcriptions checked cell by cell. Those checks establish neither complete
claim coverage nor eligibility for automatic publication.

The [first-pass source review](FIRST-PASS-REVIEW.md) compares all 25 evidence
entries with official pages and records material route, rate-year, deadline and
wording issues. It is an agent comparison, not human verification and not an
executed publication gate.

## Assurance under the revised policy

Every existing `verified_at`, `verified_by` and `last_verified_at` remains
`null`: no human verification is claimed. D-09 removes mandatory human
approval, but no fixture currently has `source_checked` assurance either. The
snapshot, validation and publication engine does not exist yet. The documented
issues must be corrected or result in a hold when that engine is built.

## Current F-criterion ledger

| Criterion | State | Evidence or gap |
|---|---|---|
| F-01 | Partly proven | 36 seed tests parse and check references; material completeness is not proven |
| F-02 | Partly proven | Real PostgreSQL round-trip and timestamp separation test; source-check timestamp is absent as expected |
| F-03 | Proven | API returns structured `opportunity_not_found` 404 |
| F-04 | Unproven | Operational schemas not built |
| F-05 | Unproven | First-pass findings documented, not machine-enforced holds |
| F-06 | Proven for fixture preview | API returns `insufficient_evidence`, null source-check metadata and `isPublished: false`; production hides the fixture |
| F-07 | Unproven | No source-failure decision contract |

The former student UI screenshots, evaluator matrix, save tests and end-to-end
walkthrough remain future S07 evidence requirements.

## T04-T05 storage and read check, 2026-10-23

`backend/app/storage/schema.sql` creates separate opportunity, programme,
round, eligibility-rule, funding-component, evidence and publication-state
tables. The fixture loader validates YAML before import, replaces an unverified
fixture atomically, skips an unchanged hash and refuses to overwrite a
source-checked record. It does not grant assurance.

Against a temporary local PostgreSQL 18 instance:

| Check | Actual result |
|---|---|
| First `python -m app.storage.load_seeds` | Loaded 4 fixtures; 4 changed |
| Second identical run | Loaded 4 fixtures; 0 changed |
| `pytest tests/test_opportunity_storage.py -q` with `SCHOLARCHECK_TEST_DATABASE_URL` | 4 passed |
| Full `pytest -q` with `SCHOLARCHECK_TEST_DATABASE_URL` | 73 passed |
| Backend wheel build | Succeeded; wheel contains `app/storage/schema.sql` |

The read response is `{opportunity, publication, isPublished}`. For a
development fixture, `publication` has `assurance:
insufficient_evidence`, null `sourceCheckedAt` and
`validationPolicyVersion`, and `freshness: not_checked`;
`isPublished` is false. The same id returns a structured 404 in production
mode. An unknown id returns `{code: opportunity_not_found, message: ...,
details: null}`; an unconfigured database returns
`{code: service_unavailable, message: ..., details: null}` with HTTP 503.

This proves read and storage behaviour, not live source checking or automatic
publication. The temporary PostgreSQL instance is test infrastructure only.
