# ScholarCheck build and release plan

Prepared 16 November 2026. Scope follows `PRP.md`, `CONTEXT.md` decisions
D-10–D-13, and `PUBLICATION-POLICY.md`. This is the execution companion to
`ROADMAP.md`; it does not expand the agreed product boundary.
Use [the local AI prompts](LOCAL-AI-PROMPTS.md) to execute this plan one bounded
task at a time, with compact context and explicit verification.

## Outcome and delivery rules

Deliver two explicit milestones:

1. **Public MVP:** a deployed, no-account scholarship website with useful,
   source-backed published records and working search, filters, details,
   official actions, sharing and problem reports.
2. **Full agreed core:** the MVP plus unattended monitoring across published
   records and bounded automatic discovery from permitted official sources.

Profiles, personal eligibility assessments, saves, comparison, notifications
and accounts remain a later product decision. Automatic applications and
match probabilities remain out of scope. A single launch record can prove the
technical flow; it must not be represented as broad degree or country coverage.

Keep the existing React/FastAPI/PostgreSQL application. Work in small batches:
implement a deliverable, verify its acceptance criteria, retain the evidence,
and move on. Fix release blockers before visual extras or new features. Do not
weaken evidence gates to meet a date or catalogue count. No human approval or
verification step belongs in routine publication.

## Baseline: reuse what exists

Code inspection finds public catalogue/detail/report endpoints, connected
home/explore/detail screens, private evidence contracts, atomic publication,
snapshot collection, separate model adapters and a one-record monitoring worker.
Docker/Compose packaging and a release smoke script also exist.

These are implemented, not proof of a live service. The repository reports
earlier local checks; the old S01 evidence ledger contains historical gaps that
conflict with newer README/roadmap status. Reconcile status using fresh checks.
The launch artifacts are recorded extraction/check outputs, not proof that the
runtime model provider has been called. RMIT remains held.

## Ordered execution backlog

| ID | Work | Depends on | Completion evidence |
|---|---|---|---|
| B01 | Establish a fresh baseline: frontend tests/lint/typecheck/build, backend tests and real disposable-PostgreSQL integration suite; record skipped tests separately | None | Dated commands/results and a short prioritized defect list; no claim that skipped integration tests passed |
| B02 | Close release-critical defects only; reconcile current status in README, roadmap and S01 evidence ledger | B01 | Passing affected checks and consistent current status; old evidence remains labelled historical |
| B03 | Prepare production configuration and deployment target: real origin/contact, database, secrets, TLS, persistent private audit storage and worker runtime | Can prepare alongside B01 | Concrete deployment configuration, required variable checklist and cost/operating limit; secrets configured outside source/chat |
| B04 | Exercise live extraction and separate evidence checking on a freshly retained official source; investigate refusal or schema failures | B01; runtime credentials/models | Retained raw/validated outputs, exact snapshot bindings, report and publish/hold decision; no invented new check time on old artifacts |
| B05 | Finalize the initial catalogue through the gate; retain all regression fixtures and unresolved holds | B04 | Every public claim supported or explicitly unknown; useful round/status presentation; held records absent from public endpoints |
| B06 | Run production packaging against PostgreSQL; deploy the web/API and database, then publish passing launch revisions | B02, B03, B05 | Successful clean build/start, health and catalogue/detail responses at the real HTTPS origin; private content/audits inaccessible |
| B07 | Verify the complete public journey and operational recovery | B06 | Deployed smoke with report/contact checks; browser proof on phone/desktop and keyboard; backup/restore and rollback procedure exercised |
| B08 | Enable one-record scheduled monitoring with live model adapters | B04, B07 | Scheduled execution history plus controlled production-equivalent changed/unchanged/failure cases; last supported facts survive failures |
| B09 | Extend monitoring to every published record and make operations observable | B08 | Per-record due times, bounded retries, concurrency/idempotency, persistent audits and actionable failure/hold visibility |
| B10 | Implement bounded official-source discovery and candidate staging | B09 | Permitted seed sources, access checks, fetch budgets, candidate identity/deduplication, provenance and private rejected/held candidates |
| B11 | Connect discovery to extraction, checking, publication and subsequent monitoring | B10 | End-to-end new-source run; supported candidate publishes once and joins monitoring; unsupported/duplicate candidates stay private |
| B12 | Run full-core release acceptance and reconcile documentation | B11 | Restart/recovery, failure and budget checks; all applicable MVP/MON/growth criteria evidenced; maintained release runbook |

## MVP acceptance gate: B01–B07

- Public HTTPS origin serves the production build; configuration persists across restarts.
- Browse, title/provider search, doctoral synonyms, country/level/funding filters,
  active-filter removal and empty/loading/error/retry states work on real data.
- Stable shared links open the same detail page; unknown IDs return the agreed 404.
- Funding components remain separate; “Fully funded” requires evidenced tuition,
  living costs and flights. Unknowns and passed/multi-stage deadlines remain honest.
- Stated eligibility is visible without implying a personal eligibility decision.
- Requirements/application links match confirmed provider destinations and round status.
- The actual check date is shown; excerpts, snapshots, reports and policy metadata stay private.
- Reports persist, show success/failure and enforce body/input/rate/origin controls;
  the operator can inspect and act on reports. Reports are not described as email delivery.
- Mobile layout, light/dark contrast, keyboard focus and dialog behavior are checked.
- Production smoke passes with `--report --require-contact`; integration tests run
  against PostgreSQL. Database and private audit backups can be restored.

## Reliable monitoring acceptance gate: B08–B09

Prove scheduled execution, unchanged content without revision/model work,
supported changes publishing atomically, unsupported changes held, fetch/model
failures preserving public facts and the real check date, bounded retries,
duplicate/concurrent runs and restart persistence. Use controlled fixtures for
failure/change drills; never alter a real scholarship claim to manufacture proof.
Retain live scheduler/provider evidence separately from simulated change tests.

The existing CLI targets one record. Add a registry/due-work dispatcher for
multiple records before claiming catalogue-wide monitoring. Add visibility for
overdue checks, repeated failures, persistent holds, model errors and report
backlog. Configure cost/request limits and a safe pause for model/discovery work.
Exercise rollback to the last supported published revision.

## Automatic growth acceptance gate: B10–B12

Start with a bounded seed set, not unrestricted crawling. Record source
identity, permission, destination and discovery method. Reuse the existing
collector, retained evidence and publication gates. Reconcile stable scheme
identity separately from programmes, rounds and intake changes. A second run
must neither duplicate opportunities nor republish unchanged candidates.

Test new candidates, conflicting claims, inaccessible sources, redirects,
duplicates, changed URLs, invalid model output and partial runs. Add rendered
capture only when an approved target actually requires it; capture failure must
hold a candidate rather than imply absence. New published records must enter
monitoring automatically. Maintain an internal decision history and bounded
work queues with retry/backoff and recovery after restart.

Broaden destination and degree coverage incrementally with evidence; the product
supports bachelor's, master's and PhD, but must never advertise coverage that the
published catalogue does not yet provide. Avoid any fixed catalogue-size launch quota.

## Pace and ownership

Suggested focused-work budget, not a deployment promise:

| Work block | Planning allowance | Result |
|---|---|---|
| Baseline and configuration preparation | 1 day | B01–B03, known release blockers |
| Live pipeline, content and release | 2–4 days | B04–B07, public MVP |
| Production monitoring and operations | 2–4 days plus scheduled observation | B08–B09, unattended updates |
| Bounded discovery and full-core acceptance | 4–7 days | B10–B12, autonomous core |

Re-estimate after B01 and the first live model run. Provider access, hosting
setup, source complexity and discovered defects can extend these allowances.
Do not count waiting for credentials or meaningful scheduled observation as
completed engineering. One implementer can follow this sequence without a rewrite.

The implementation work includes configuration templates, fixes, deployment
preparation, checks and retained evidence. Owner inputs needed for external
execution are the hosting account/target, public origin, real contact address,
runtime model access and acceptable operating budget. Prepare everything that
does not depend on those inputs first. Never invent addresses or credentials.

## Immediate next work

Fresh local checks on 16 November 2026: backend **239 passed, 18 skipped**
(database integration proof remains outstanding in this run); frontend **76
passed**, lint passed, and production build including TypeScript checking
passed. Backend emitted a test-client deprecation and a serializer warning;
triage these without treating them as demonstrated production failures.

Start B01, record exact results, then fix the smallest set of confirmed release
blockers. Prepare B03 alongside that work. The next product milestone is a
verified public MVP URL; the next operational milestone is one scheduled record
with proven safe updates/holds. Neither is complete merely because code exists.
