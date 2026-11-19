# Evidence — S01 foundation

## B04 rehearsal — 19 November 2026 (credential-free half only)

No `OPENAI_API_KEY` exists in this workspace, so no model was called and no live
extraction or checking pass ran. The published report keeps its
`2026-11-03T18:40:32Z` check time and nothing below is new evidence. Timestamps
are the collector's own records.

| Check | Actual result |
|---|---|
| Fresh collection | `app.collect.snapshot.collect` on the registered CGRS D URL: 200, 24,287 characters, robots "no matching rule", `retrievedAt 2026-11-19T11:14:55Z` |
| Text unchanged | Body sha256 `dcfbf661b0e980cc7a7425bfe9d5177e385f9b4073c90f1ed3fc4c533e26e90b` in both readings, same snapshot id; raw bytes 55,734 → 55,703 with raw hash `cda51a41…` → `86dd11e3…` |
| Re-retention | `write_artifact` into `content/snapshots` raised `SnapshotExists(same_text=True)`; the tracked file's sha256 `3f276bae…` was identical before and after |
| Command adapters | Stub adapters logged their stdin: extraction `{task, instructions, snapshots: 1, previous_record: null, schema: ExtractionProposal}`; checking `{task, instructions, candidate: 24 facts, snapshots: 1, schema: present, no top-level title}` |
| Replay | Decision `publish`, `assurance: source_checked`, 18 checks, content hash `92a21dafd0bf40e5b18ce7d7476bfebeec4e1dd0020fbbcacc60fc1d9b41de71` equal to the published report, `checked_at 2026-11-19T11:15:24Z` — a rehearsal over recorded outputs, never published |
| Hold | One verdict forced to `unsupported`: decision `hold`, `assurance: insufficient_evidence`, reasons naming the fact and the snapshot without a supported quote |
| Refusals | No adapter configured: exit 1, `Configure EXTRACT_COMMAND or its model and OPENAI_API_KEY`, no audit directory. Text altered under the same id (`$40,000 per year` → `$30,000 per year`): `component:cgsd-living-support.amount: the quoted span is not in the retained snapshot` |

Artifacts live under the gitignored `var/b04/`; `var/b04/negative-fixtures/`
holds the altered snapshot and verdict with a README saying they are not
evidence. No database was used: `DATABASE_URL` was unset and `--publish` was not
passed.

## Baseline re-verification — 16 November 2026

Task B01 re-ran the checks instead of restating earlier numbers. `git status`
was clean at HEAD `1188df8`; no product code changed.

| Check | Command | Actual result |
|---|---|---|
| Backend suite, no database | `cd backend && .venv/bin/python -m pytest` | **239 passed, 18 skipped**, 1 warning |
| Backend, disposable PostgreSQL | `psql -h localhost -d postgres -c 'CREATE DATABASE scholarcheck_test_b01'`, then `SCHOLARCHECK_TEST_DATABASE_URL=postgresql://localhost/scholarcheck_test_b01 .venv/bin/python -m pytest -rs` | **257 passed, 0 skipped**, 1 warning |
| Frontend tests | `cd frontend && npm run test` | **76 passed** in 11 files |
| Typecheck, lint, build | `npm run typecheck`; `npm run lint`; `npm run build` | all passed, no diagnostics |

The 18 tests skipped without a database are the integration tests listed in
[the build checkpoint](../../BUILD-CHECKPOINT.md); with the disposable database
configured all 18 ran and passed, so the earlier "database integration proof
remains outstanding" note is closed as of this date. The disposable database was
dropped afterwards and left no schemas behind. Environment: Python 3.14.2,
Node 24.21.0, PostgreSQL 18.6.

Only one warning reproduced: FastAPI/Starlette's `httpx` test-client
deprecation, which affects test tooling only. The serializer warning recorded in
the 5 November entry below did not reappear in any of three runs. Docker is
still not installed here (`docker: command not found`), so the container build
remains unexecuted. No failing test, lint, typecheck or build step was observed;
the open items are external ones — deployed origin and contact, container
build/start, a live model call and unattended monitoring.

## Acceptance result — 5 November 2026 (historical)

This section superseded the implementation-status claims in the entries below
at the time it was written, and is itself superseded on execution dates by the
16 November baseline above. Those entries record what was proven under earlier
policies.

| Requirement | Current proof |
|---|---|
| Structured validation and auditing | Policy `.3`: explicit fact states; evidence per field and reading; separate extraction/checking adapters; candidate, fact-table and full snapshot fingerprints; retained proposals, adjudications, reports and decisions |
| Publication correctness | Decimal/token amount checks reject misleading substrings, misplaced decimals, negative values and percentages; currency, period, rate year, route, associated source row, conflicts and coverage checks; public prose/programme/round-label fact coverage |
| One real publication | CGRS D proposal and source-context adjudications in `content/publication/cgrs-d/complete-run/`; real PostgreSQL publication, unsupported-claim hold and immutable revision tests; RMIT still returns 404 |
| Public API/UI | Published-only list/search/filter/detail in all environments; explicit response allowlist; public API omits evidence, snapshot/report/policy/revision metadata; browser loads real records; loading/retry/report-failure UI tested |
| Launch reporting | Problem reports persist in PostgreSQL with origin checks, input bounds, an 8 KiB body cap and five-per-hour address-hash limit; source-check dates and official links shown |
| One-record monitoring | Real PostgreSQL tests for unchanged content, unsupported changed amount held, supported changed amount published, duplicate fetch skipped, failure/retry scheduling and prior-revision preservation |

Executed checks:

- Backend: `SCHOLARCHECK_TEST_DATABASE_URL=postgresql://127.0.0.1:55439/postgres .venv/bin/python -m pytest --tb=short` — **257 passed**, no skips. Two existing/test-only warnings: FastAPI's httpx deprecation and a deliberate malformed URL model-copy serializer warning.
- Frontend: typecheck, ESLint and production build passed. **76 Vitest tests passed**, including API loading/retry and report delivery/failure. Homepage wording and actual check-date assertions follow the public evidence boundary.
- Local production HTTP smoke: `python3 scripts/smoke.py http://127.0.0.1:8017 --report` — **passed**, including one accepted persisted report, public catalogue/detail, empty search, and RMIT's 404. Contact was not configured and `--require-contact` was not asserted.
- Native Safari walkthrough against that production build: homepage showed the real CGRS D record and actual check date; Canada filter returned one record; detail showed unspecified currency, yearless agency deadline with “Confirm with provider”, official link and no internal quotations; report submission closed the dialog and showed **“Report received. Thank you.”**
- CGRS D was published into disposable PostgreSQL. The final local revision is 2 because the initial run was followed by the expanded public-prose audit. Fresh isolated integration schemas publish it as revision 1. This is local proof, not an internet release.

Important limits:

- `complete-run` uses explicit extraction and independent source-context checking outputs produced during this Codex source review. No paid/live Responses API call is claimed. The built-in adapter has injected transport/refusal tests; production requires API credentials and explicitly selected model IDs, or configured command adapters.
- No hosting target/domain or real public contact address has been supplied. The contact UI is configurable; no address was fabricated. A public deployment and deployed smoke check remain outstanding.
- Docker is not installed in this workspace. Dockerfile/Compose and the optional scheduled monitor service are supplied, but their container build has not been executed here. The native production build was executed.
- The gate intentionally holds unsupported currency abbreviations, ambiguous source-table associations or unrecognized qualifier formats. A held candidate needs better retained evidence or extraction, not a relaxed assertion.

See [deployment and monitoring instructions](../../DEPLOYMENT.md). The
`first-pass-review.json` RMIT finding has not been removed or weakened.

## Historical evidence


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
shape, separate retrieval timestamps (the human-verification fields they once
carried have since been removed), and intentionally unspecified
values. The 2026-10-23 content pass recorded 13/13 source URLs responding and
19 passages matching after whitespace normalisation, plus six table
transcriptions "checked cell by cell". That last category was the weak point: a
transcription is not a quotation, so nothing could match it against a page. The
2026-11-02 collection below replaced every transcribed passage with a verbatim
span of a retained snapshot.

The [first-pass source review](FIRST-PASS-REVIEW.md) compares all 25 evidence
entries with official pages and records material route, rate-year, deadline and
wording issues. It is an agent comparison, not human verification and not an
executed publication gate.

## Assurance under the revised policy

Human verification is gone from the active contract: the `human_verified`
assurance level, `Evidence.verified_at`/`verified_by` and
`Opportunity.last_verified_at` were removed from the model, the fixtures and
the schema, and a migration demotes any pre-gate row to
`insufficient_evidence` with `needs_recheck`. No fixture has
`source_checked` assurance. The gate that can grant it now exists; one candidate
is still held by a recorded finding and the other three cannot publish without a
validation report.

## Launch candidate collection, 2026-11-02

`backend/app/collect/` collects a page the way the policy requires: read
`robots.txt` first, refuse a disallowed page without fetching it, fetch once,
keep the readable text, and write an artifact recording the request URL, every
redirect hop, the final URL, the HTTP status, the raw-response hash, the retained
hash, the robots decision, the user agent and the parser version. Snapshot ids
are content-addressed, so changed text becomes a new snapshot rather than an
overwrite of evidence a report may already cite, and an unchanged page fetched
again writes nothing: the retained file keeps the time and hashes a report was
checked against.

Redirects are followed by the collector, not by the HTTP client, so the address
that answers is checked against its own access rules before it is fetched. A hop
the rules refuse ends the collection, and a client that hides a hop is an error
rather than something to record.

Seven pages were retained for the four candidate records. All answered 200, and
all were permitted by their access rules:

| Record | Retained pages |
|---|---|
| CGRS D | the funding-opportunity page on `nserc-crsng.canada.ca` (the old `nserc-crsng.gc.ca` address now redirects there) |
| UdeM exemption | the `registraire.umontreal.ca` exemption page, 3e-cycle section |
| RMIT stipend | stipend page, research-scholarships landing page, HDR terms and conditions |
| Sydney RTP | international RTP page, RTP overview page |

All 25 passages now occur verbatim in the retained text, and each fixture's
`retrieved_at` equals the snapshot's. Corrections the real pages forced:

- **CGRS D** recorded only the direct-to-agency route. The page states both
  routes, and that the institutional one is "significantly earlier"; the record
  now carries both rounds and cites the canonical host.
- **UdeM** recorded the exemption as automatic with admission. The page
  conditions it on every eligibility bullet — admission offer, CAQ and study
  permit, full-time enrolment, no other exemption, no external funding — so the
  route now says "once every eligibility condition is met" and the cited passage
  is the conditional sentence.
- **Sydney** recorded only the round whose deadline had already passed. The
  retained table also lists Research Period 3 and 4, 2027 (deadline 18 December
  2026) and Research Period 1 and 2, 2028 (10 September 2027); all three rounds
  are recorded against that one table.
- **RMIT** now carries the 2027 round with the deadlines the retained table
  states (international EOI 30 August 2026, full application 30 September 2026).
  Both have passed, while the same page still says applications for 2027 are
  open and the stipend page says the 2027 rate had not been released, so the
  round cannot be presented as open or priced for 2027. The record keeps the
  published dates and the round stays held.

Holds: three findings were removed only after the corrected claim was re-checked
against a retained snapshot. The RMIT round stays in
`content/publication/first-pass-review.json`, so `publish` holds that record. The
other three have no open finding, but none can publish yet: publishing needs a
validation report for its exact revision, and no extraction run has produced a
candidate for these fixtures — the passes that would write a report exist in
`app/publication/`, but no model has been called and no report is retained.

Limits of this pass:

- Extraction is text-only. A page that builds its content in the browser yields
  chrome and static text instead of the rendered view, and none of these seven
  pages was checked for that failure mode beyond reading the retained text: if a
  table is missing from a body, that is a collection gap, not evidence of
  absence. The RMIT calendar was first read as missing and then found in the
  retained body; the snapshot-against-fixture check is what caught that error.
- A snapshot proves what was served, not that the page is right, and not that a
  claim applies to the recorded applicant category, round or rate year. That
  judgement is what `publication/evidence_check.py` is for: it refuses a verdict
  that quotes a span the fact does not carry, or that places the quote in a
  round or degree level the record does not have. It has not been run against
  these seven pages, so no applicability judgement exists yet.
- None of the seven pages redirected, so the hop-by-hop rules check has only been
  exercised against a local test server, not against a real move between hosts.
  The NSERC address in the table above is the one that answered; the redirect
  from the old `.gc.ca` address is a property of the site, not something a
  snapshot records.
- The approved-host list moved from `nserc-crsng.gc.ca` to
  `nserc-crsng.canada.ca`. A citation that keeps the old address now holds,
  because the retained snapshot records the address that actually answered.

## F-criterion ledger as recorded 2026-11-02 (historical)

These rows predate the published-only API, problem reports and launch reporting
recorded above; read F-09 and F-12 there rather than here. The ledger is kept
unchanged to preserve what was proven on that date.

| Criterion | State | Evidence or gap |
|---|---|---|
| F-01 | Partly proven | 36 seed tests parse and check references; material completeness is not proven |
| F-02 | Proven | Real PostgreSQL round-trip; the check time is stored separately from retrieval and only set with a revision; migration test demotes `human_verified` and a source check without a revision |
| F-03 | Proven | API returns structured `opportunity_not_found` 404 |
| F-04 | Proven | `app/publication/contracts.py` defines `SourceSnapshot`, `Applicability`, `ClaimCheck`, `ValidationReport`, `PublicationDecision` and `PublishedRevision`, `facts.py` adds the three-state material-fact table and `candidate.py`/`evidence_check.py` the separate extraction and check outputs; tests reject invalid states, and no human-verification state can be constructed |
| F-05 | Proven | `content/publication/first-pass-review.json` records each open finding; `publication/register.py` reads it and `store.publish` loads it itself, so a report claiming support — and no argument that could leave the findings out — still holds the record. Three findings were cleared only after the corrected claim was re-checked against a retained snapshot; the RMIT round remains held |
| F-06 | Proven | API returns `insufficient_evidence`, null check metadata and `isPublished: false` for a preview; production hides it; after a real publish it returns `source_checked` with the check date |
| F-07 | Unproven | No source-failure decision contract |
| F-08 | Partly proven | Gate and atomic publish proven against retained snapshots and reports; an HTML/text collector now retains seven launch-source snapshots with provenance, and every fixture passage is checked against them. The extraction and evidence-check passes exist and are tested against their own refusal cases, but no model run has produced a report for a launch record; JavaScript-rendered capture and a real publish are outstanding |
| F-09 | Unproven | Only development/test detail read exists; no public catalogue or filters |
| F-10 | Partly proven | Local UI tests cover browse, filters, detail, stated eligibility, rounds, the official requirements and application links and shareable hash URLs with no account; the deployed smoke check is outstanding |
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
`sourceCheck` is `null`, so no view can imply `source_checked` assurance. The
detail view shows no source-check panel at all — no check date, no result, and
no "confirm with the provider" reminder — so the record's status cannot read as
a claim about the source.

| Check | Command | Actual result |
|---|---|---|
| Frontend tests | `cd frontend && npm test` | 69 passed in 10 files |
| Typecheck | `npx tsc -b --force` | No errors |
| Lint | `npm run lint` | No problems |
| Production build | `npm run build` | Built; no preview data in the bundle (`RMIT` and the fixture amounts are absent from `dist/assets`) |

What the tests establish, and what they do not:

- Search and filters run over the derived records. Funding type is computed
  from the three coverage facts, so a record is “Fully funded” only with
  tuition, living costs and flights all `stated`; a stored label cannot
  override that. Passed-round notes come from a round's published status, not
  from a guessed date.
- A record shows components separately, without a computed total, and lists the
  eligibility conditions as published. Quoted passages, source addresses and
  saved dates are no longer shown; the official page link and the application
  step sit under “Rounds and deadlines”. The application button follows the
  recorded route and the rounds rather than its styling: an unconfirmed route
  and a record whose deadlines have all passed get no button, and a record with
  no separate scholarship application says “Apply for admission”. Catalogue
  tests still fail if a retained reference does not resolve.
- Hash routes keep `#cgsd-doctoral` and `#explore?c=Canada` shareable, and an
  unknown id says the record is unavailable instead of inventing one.
- The report dialog closes and states that nothing was sent, because no
  feedback endpoint exists yet (F-12). Branding and contact details remain
  placeholders.
- This is local UI proof only. No record is published. The published-only
  public API and the deployed smoke check for F-09/F-10 are still outstanding.

## Automated publication gate, 2026-10-31

`backend/app/publication/` now decides whether a candidate may become public
and writes the result atomically. Human verification was removed first, so
nothing — a person, an agent note or a successful fetch — can grant assurance:
`PublicationAssurance` has two values, and the fixtures, model and schema carry
no `verified_at`, `verified_by`, `last_verified_at` or `human_verified`.

The decision is pure (`gates.evaluate`). A record is published only when:

- the report names the same opportunity and the same canonical content hash as
  the candidate, under the current `POLICY_VERSION`;
- every check cites a supplied, retained snapshot from an approved provider
  host, with the same URL and retrieval time as the evidence entry;
- every cited excerpt and every displayed passage still occurs in the snapshot
  (exact wording; only whitespace is collapsed);
- every evidence entry is covered, no claim has two different excerpts, and
  every stated amount appears in the passage that backs it;
- the candidate has no open review finding. The findings from
  `content/publication/first-pass-review.json` are read by the gate itself
  (`publication/register.py`) and loaded inside `store.publish`, which has no
  argument that could leave them out. A finding holds the record it names and
  any record citing the same page, and a register that cannot be read holds
  every candidate, so neither a supporting report nor a deleted file clears a
  held record.

`store.publish` then writes, in one transaction, the snapshots, the live facts,
an immutable revision carrying the report and snapshot references, and the
`source_checked` state tied to that revision. A held or rejected candidate
raises `PublicationBlocked` before any write; a failure inside the transaction
leaves no trace. Snapshots are immutable in the database, and the state
constraints refuse `source_checked` without a revision.

| Check | Command | Actual result |
|---|---|---|
| Backend suite with PostgreSQL | `SCHOLARCHECK_TEST_DATABASE_URL=postgresql:///scholarcheck_test .venv/bin/python -m pytest` | 228 passed |
| Backend suite without PostgreSQL | `.venv/bin/python -m pytest` | 214 passed, 14 skipped |

What the tests establish, and what they do not:

- A supported candidate publishes its revision, report and snapshot links, and
  the production read endpoint then serves it as `source_checked` with the
  actual check date.
- An unsupported claim, an unclear claim, an excerpt missing from its snapshot,
  a missing or unchecked evidence entry, a conflicting excerpt, an amount the
  passage does not state, a stale retrieval time and a mismatched page each
  hold the candidate. An unapproved host, another revision's report and
  evidence the record does not carry are rejected.
- The real RMIT fixture cannot be published: with a report that claims support
  for every entry, and with no argument in `publish` that could omit the
  findings, `publish` holds it and no snapshot, revision or opportunity row is
  written; the production endpoint answers 404. A copy under a new id is held
  just the same, because the hold follows the page the finding was raised on.
  A register that cannot be read holds every candidate.
- `evaluate` has no default for `register`, so the check cannot be skipped by a
  caller that simply says nothing; a test asserts the parameter's absence.
- A fact table that leaves an obliged field out, states a value the record
  contradicts, quotes a span the retained page lacks, reads from evidence the
  record does not carry, or names a part the record does not have each stops
  publication. A stated fact counts as covered only when a supported verdict
  quotes one of its own spans, and a verdict may not be placed in a round or
  degree level the record lacks.
- Every seed fixture carries a fact for every field its record obliges and
  reaches `publish` against a supporting report with an empty register, so a
  fixture's hold is always its recorded finding rather than a gap in its facts.
  Amounts are stated only where the cited passage carries their digits; a rate
  year, or a deadline the pages do not give, stays `unspecified` with a reason.
- A publish that fails halfway rolls the snapshot and revision writes back.
- A pre-gate database is migrated: `human_verified` rows become
  `insufficient_evidence`/`needs_recheck`, and the level can no longer be
  stored.
- The gate cannot establish editorial truth. It proves that a quoted span
  exists, that values match it and that the report covers every claim; it
  cannot prove the surrounding context means what the claim says. That is what
  the separate evidence-check pass is for, and why the review findings are read
  by the gate itself rather than trusted to appear in the report. That pass now
  exists in `publication/evidence_check.py`, but it has never been run against
  the launch pages, so no report it writes has been reviewed.
- No launch record is published. Source-failure handling (F-07), a real model
  run of the extraction and evidence-check passes, JavaScript-rendered capture,
  the published-only catalogue API and the deployed smoke check remain
  outstanding. The collector, seven retained snapshots, the material-fact table
  and both passes now exist (see the collection section above).

## Public evidence boundary, 2026-11-01

Owner decision D-13 keeps claim-linked passages, snapshots and validation
reports in the backend. Published pages will show the actual check date, a plain
source-check result and official provider links, without an evidence-reading
interface. The current development frontend already omits the passages and
source-check panel; it must only show a checked date for a truly published
record. The existing detail API returns the full `Opportunity`, including
evidence, so the future published-only public response still needs a smaller
shape that omits internal evidence. This is an outstanding F-09 response-shape
check, not completed UI or API proof.
