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

## Current F-criterion ledger

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
