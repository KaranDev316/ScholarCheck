# ROADMAP.md — Autonomous scholarship platform

Inputs: `CONTEXT.md`, `PRP.md`, `PUBLICATION-POLICY.md`. Rebased on owner
direction D-09, 23 October 2026. The earlier user-journey-first roadmap is
superseded; existing code and the four YAML fixtures remain useful.

## Sequence and proof

| Slice | Deliverable | Proof before moving on |
|---|---|---|
| S01 — Foundation (current) | Domain/evidence model; four regression fixtures; PostgreSQL storage and read API; source-check and publication decision contracts | Fixtures load and expose facts without claiming human verification or automatic assurance; missing/contradictory material claims are identified |
| S02 — Source monitoring | Source registry, permitted fetches, immutable snapshots, conditional requests where supported, scheduler and retry | Re-fetch four official sources; unchanged content yields no duplicate work; fetch failure retains the previous snapshot |
| S03 — Candidate extraction | HTML/PDF parsers, optional model-assisted extraction, field-level evidence mapping | Amount, rate year, route, deadline and restrictions are traceable to snapshot passages or table cells; unknowns stay unknown |
| S04 — Validation and publication | Deterministic gates, hold/reject reasons, duplicate checks, atomic revisions, `source_checked` assurance | Same snapshot gives same decision; known fixture issues hold; fully evidenced candidate publishes without a human click |
| S05 — Change and freshness | Detect material changes, publish safe revisions, retain last-known-good, warn on source failure | Changed source produces an explained revision or hold; failed fetch never silently closes a scholarship |
| S06 — Discovery | Find official opportunities, reconcile identities and duplicates, widen source coverage | New source enters through the same gates; duplicate candidates do not create duplicate listings |
| S07 — Student experience | Search/filter, profile-based eligibility, funding, deadlines, evidence/assurance labels, saving, comparison and notifications | Student sees limitations and source state, can follow the complete decision path; account sync remains deferred |
| S08 — Operations and release | Monitoring, automatic retries, failure alerts, quality metrics, usability study and 20-30 source-checked records | Pipeline runs unattended in normal cases; unsupported claims and stale records are measured; release criteria in PRP pass |

SYS-01..SYS-08 span S02-S08. REQ-01..REQ-12 are completed in S07
(with source freshness foundations in S05); exceptional maintainer
actions in REQ-13 belong to S08. REQ-14 account sync remains deferred.

No slice may publish unsupported facts merely to meet catalogue size or schedule.
The first milestone is the four-source unattended re-fetch and decision
demonstration, not a polished user-facing catalogue.

## S01 remaining work

| ID | Task | State |
|---|---|---|
| T01 | Scaffold frontend/backend and test runners | Complete |
| T02 | Shared `Opportunity`, `Evidence`, `Profile` and assessment types | Complete as a draft contract |
| T03 | Four YAML fixtures and seed validation tests | Complete as unverified regression inputs; source review found issues |
| T04 | PostgreSQL schema and fixture loader/read model | Not started |
| T05 | Opportunity read endpoint and not-found response | Not started |
| T06 | Source-check and publication decision **contract** with explicit machine versus human metadata | Not started |
| T07 | Deterministic fixture audit: known route/rate/deadline discrepancies must be held, not labelled publishable | Not started |
| T08 | S01 regression and evidence report for storage/read and hold decisions | Not started |

The former T06-T11 evaluator, profile and frontend tasks move to S07. The
proposed assessment API in `slices/S01/PROPOSED-CONTRACTS.md` is preserved for
that work; its gate does not block S01 storage/read. S01 has no automatic
publication engine; that is S04. S01 defines the policy contract and test
benchmarks it must obey.

## Decisions that remain open

- Source registry allowlist and access rules before S02 fetching.
- Snapshot storage provider and retention before S02.
- Whether a model-assisted extractor is needed after deterministic parsers are
  tried in S03.
- Authentication for optional maintainer actions; it cannot be a dependency of
  routine publication.
- Hosting, operating budget and final source/destination set.

The publication policy itself is settled by D-09: human approval is optional,
human-verification fields remain human-only, and failed automatic gates hold or
preserve the last-known-good record.
