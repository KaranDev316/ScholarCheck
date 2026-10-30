# Evidence — S01 foundation

Status: **in progress under D-09..D-11**. Personal assessment criteria
AC-01..AC-14 are deferred. Current S01 criteria F-01..F-12 are in
`VERIFICATION.md`. This file preserves completed scaffold and fixture checks
and records what remains unproven.

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
`null`. D-11 removes human verification from the product direction, but those
legacy fields still exist in code and fixtures; migration is unproven. No
fixture currently has `source_checked` assurance. The snapshot, validation
and publication engine does not exist yet. Documented issues must be corrected
or result in a hold when that engine is built.

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
| F-08 | Unproven | No retained snapshots or publication gate; all four fixtures remain unpublished |
| F-09 | Unproven | Only development/test detail read exists; no public catalogue or filters |
| F-10 | Partly proven | Local UI tests cover browse, filters, detail, stated eligibility, rounds, exact evidence, official links and shareable hash URLs with no account; the deployed smoke check is outstanding |
| F-11 | Partly proven | Coverage checklist plus a computed classification that only says “Fully funded” when tuition, living costs and flights are all stated, with tests; no published record exercises it yet |
| F-12 | Unproven | No feedback endpoint or production brand/contact details |

Personal evaluator, save and comparison proof remains future work. Public
catalogue/detail proof is now part of S01.

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

## Frontend cleanup, 2026-10-24

The visitor-facing API health panel, Vite starter favicon and unused personal
assessment TypeScript mirror were removed from the frontend. The backend
health endpoint remains available for operations. The landing page now states
that no scholarships are published, without displaying environment details.
The wireframe reference uses text controls and no SVG icons; disconnected
preview actions are labelled as such.

At this earlier stage, the frontend check passed: 1 test, typecheck, lint and
production build. The 7-test result above is historical scaffold evidence; its
health-client tests were removed with that startup-only UI.

## Public catalogue UI, 2026-10-30

The frontend now implements the home, explore and detail views from
`docs/design/scholarcheck-product-wireframe.html` over the four S01 fixtures,
as development previews: every screen says the record is not published and
`sourceCheck` is `null`, so no view can imply `source_checked` assurance.

| Check | Command | Actual result |
|---|---|---|
| Frontend tests | `cd frontend && npm test` | 56 passed in 9 files |
| Typecheck | `npx tsc -b --force` | No errors |
| Lint | `npm run lint` | No problems |
| Production build | `npm run build` | Built; no preview data in the bundle (`RMIT` and the fixture amounts are absent from `dist/assets`) |

What the tests establish, and what they do not:

- Search and filters run over the derived records. Funding type is computed
  from the three coverage facts, so a record is “Fully funded” only with
  tuition, living costs and flights all `stated`; a stored label cannot
  override that. Passed-round notes come from a round's published status, not
  from a guessed date.
- A record shows components separately, without a computed total. Components
  and eligibility statements can point at numbered evidence passages kept with
  source URLs and save times. Catalogue tests fail if a supplied reference does
  not resolve; they do not require every statement to have a reference.
- Hash routes keep `#cgsd-doctoral` and `#explore?c=Canada` shareable, and an
  unknown id says the record is unavailable instead of inventing one.
- The report dialog closes and states that nothing was sent, because no
  feedback endpoint exists yet (F-12). Branding and contact details remain
  placeholders.
- This is local UI proof only. No record is published. The published-only
  public API and the deployed smoke check for F-09/F-10 are still outstanding.
