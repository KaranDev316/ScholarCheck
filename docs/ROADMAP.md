# ROADMAP.md — Scholarship MVP, then reliable monitoring

Inputs: `CONTEXT.md`, `PRP.md`, `ARCHITECTURE.md`,
`PUBLICATION-POLICY.md`. Owner decisions D-10..D-12 set the sequence below.
The four current fixtures remain unpublished
regression inputs until their material claims pass the publication policy.

## Stage 1 — Make it work (finish S01)

Publish a small set of the best-evidenced scholarships with a usable public
website. The four existing fixtures are candidates, not a launch quota. No
account is required.

| Order | Deliverable | Exit proof |
|---|---|---|
| 1 | Select launch records from government, university or approved scholarship NGO sources; audit the four fixture issues and replace weak launch candidates | Every displayed material claim has an internal reference to an exact retained passage or table cell; unsupported candidates remain private and all four fixtures stay in regression tests |
| 2 | Build the public UI shell from the wireframe while publication work proceeds | Home, Find scholarships and detail routes work with clearly marked development data, responsive layouts and empty/loading/error states; no fixture is presented as published |
| 3 | Migrate legacy human-verification fields and finish the validation/publication path | Contracts, an atomic report-and-snapshot-backed publish, the fixture-hold register, the stated/unspecified/conflicting fact table and the separate extraction and evidence-check passes are done; a real run of those passes must still produce auditable proposals for a launch record, and code must keep enforcing provider, exact excerpt, value, date, conflict, applicability and coverage gates |
| 4 | Complete published-only list, search, filter, detail and feedback APIs and connect the UI | Country, study level and funding-type filters work on published records; official actions, sharing and problem reports work; unknown IDs return the agreed 404 |
| 5 | Run release checks and deploy | Every launch record is source-checked, first-release journeys work at the deployed URL, and real branding/contact details replace placeholders |

The release target is evidence quality. If a source cannot support a material
claim, hold or replace that candidate. No human-verification path exists.
UI work starts before the publication pipeline is complete, but the public
catalogue stays empty until records pass the gate.

## Stage 2 — Make it update itself

Monitor **one** of the published scholarships first. Fetch its registered
official source on a schedule, retain an immutable snapshot, and compare it to
the last checked version. Unchanged content does no publication work. A
meaningful change creates a candidate that runs through the same evidence and
validation gates as initial publication.

The worker either publishes an explained revision or holds it with a reason.
Fetch failures and uncertain changes keep the last supported public record
and its checked date while recording an internal recheck state. Retries,
duplicate processing and audit history
must be tested. This stage is complete when a material change is detected,
validated, and safely updated or held without owner intervention.

After that proof, extend monitoring to the other published records.

## Stage 3 — Make it grow itself

Add official-source discovery, extraction of new candidates, identity and
duplicate reconciliation, and automatic publication through the existing
gates. Expand beyond the launch set only after Stage 2 is reliable.

## Deferred from the first release

Applicant profiles and personal eligibility assessments, saved items,
comparison, checklists, notifications, accounts, and catalogue-size targets
remain later work. The first release displays **stated eligibility**; it does
not decide whether a particular visitor qualifies. Automatic application
submission and match probabilities remain out of scope.

## Current implementation

The React/FastAPI scaffold, four YAML fixtures, PostgreSQL loader, and a
development-only detail read endpoint exist. The publication contract, gate and
atomic publish exist, and an HTML/text collector with seven retained
official-source snapshots now backs every fixture passage. The material-fact
table, the candidate extraction pass and the separate evidence-check pass are
implemented and tested, but no model run has produced a report for a launch
record. JavaScript-rendered capture, the public list/search API, the public
listing UI and the source monitor do not yet exist.
Human-verification fields are gone and material facts are stated, unspecified or
conflicting rather than possibly null. The S01 evidence ledger records
completed checks and outstanding proof.
