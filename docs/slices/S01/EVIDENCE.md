# Evidence — S01

Status: **in progress.** Step 1 (scaffold) and Step 2 T03 (seed format and
fixtures) are recorded below; no acceptance criterion is proven yet.

Per `VERIFICATION.md` section 8, each acceptance criterion needs an artifact.
Record them here as the slice progresses:

- AC-01..AC-03: profile form component tests + screenshots, storage inspection.
- AC-04: listing component test, link check, screenshot.
- AC-05: API 404 example (`{code: "opportunity_not_found"}`), UI screenshot.
- AC-06..AC-09: evaluator matrix test output, UI screenshots.
- AC-10: data-to-UI test output, screenshot.
- AC-11: evidence-panel test, screenshot.
- AC-12, AC-13: storage-fixture tests, storage inspection.
- AC-14: forced-failure test, screenshot.

Step 1 artifacts (scaffold only). Proposed API shapes awaiting the T02/T07 gate
are in `PROPOSED-CONTRACTS.md`; they are not part of `VERIFICATION.md` §5 yet.

| Check | Command | Result |
|---|---|---|
| Backend tests | `cd backend && .venv/bin/python -m pytest` | 27 passed |
| Frontend tests | `cd frontend && npm run test` | 7 passed |
| Type check | `cd frontend && npx tsc -b --force` | exit 0 |
| Lint | `cd frontend && npm run lint` | exit 0 |
| Production build | `cd frontend && npm run build` | built |

No acceptance criterion is proven by Step 1: it adds no listing, profile form,
evidence panel or save behaviour. Fixture data is still unverified against
official sources and remains a release blocker for S01.

## Step 2 (T03) — seed format and fixture records, 2026-10-23

Format v1 is written in `content/opportunities/README.md`: one file per
opportunity, top-level `Opportunity` object, `snake_case` keys matching
`backend/app/domain/models.py`, quoted decimal amounts, evidence with separate
`retrieved_at`/`verified_at`, `unspecified` instead of zero or an estimate.
`pyyaml` is now declared explicitly in `backend/pyproject.toml` (it was already
present transitively through `uvicorn[standard]`).

| Fixture | Demo shape it covers | Official source used |
|---|---|---|
| `cgsd-doctoral.yaml` | Enrolment-only doctoral award; living support only, no tuition line | [NSERC CGRS D](https://www.nserc-crsng.gc.ca/students-etudiants/pg-cs/cgsd-bescd_eng.asp) |
| `udem-exemption-doctoral.yaml` | Tuition exemption: `tuition_reduction` with 24 067,80 CAD/year; living support `unspecified` | [UdeM exemption](https://registraire.umontreal.ca/droits-de-scolarite/bourse-exemption/) |
| `rmit-research-stipend.yaml` | Two-stage round (EOI, then full application) with stipend, international fee offset and relocation allowance | [RMIT scholarships](https://www.rmit.edu.au/research/research-degrees/scholarships), [RMIT stipend](https://www.rmit.edu.au/scholarships/research/research-stipend), [RMIT T&Cs](https://www.rmit.edu.au/research/research-degrees/terms-and-conditions) |
| `usyd-rtp-stipend.yaml` | Stipend plus fee offset plus health cover, each a separate component | [RTP international](https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html) |

| Check | Command | Result |
|---|---|---|
| Seed content tests | `cd backend && .venv/bin/python -m pytest tests/test_seed_content.py` | 36 passed |
| Full backend suite | `cd backend && .venv/bin/python -m pytest` | 69 passed |
| Evidence and link check | `curl -L -o /dev/null -w '%{http_code}'` on every `links`/`evidence` URL | 13/13 returned 200 |
| Passage spot-check | normalise whitespace and search each passage in the retrieved page text | 19 quoted passages matched verbatim; 6 marked table transcriptions checked cell by cell |

Coverage of the data model by tests: models accept each file; ids unique and
every evidence reference resolves; every blocking rule is evidenced; any
component that states a value is evidenced; `unspecified` components carry no
amount or currency; no `total`/`sum` field exists on `FundingComponent`; rounds
expose identity only.

### Fixture verification status (A2 still open)

Every `evidence.verified_at`, `verified_by` and `last_verified_at` is `null`:
the values were retrieved from the official pages on 2026-10-23 by an agent, not
confirmed by a human. **A2 is therefore not met and the fixture set remains a
release blocker**, as `PLAN.md` Step 6 requires it to be recorded. A reviewer
sets those fields after checking each passage (checklist in the content README);
the tests assert the current, unverified state so a silent claim of verification
cannot slip in.

Not part of T03: PostgreSQL schema and loader (T04), the opportunity read
endpoint with `opportunity_not_found` (T05).
