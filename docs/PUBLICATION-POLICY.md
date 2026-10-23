# Publication policy — autonomous, evidence-first

Status: **product direction approved 23 October 2026; implementation pending**.
This policy replaces mandatory human approval for routine publication. It does
not declare the current YAML fixtures publishable.

## Assurance and timestamps

| Label | Meaning | Who may set it |
|---|---|---|
| `source_checked` | Every required automated gate passed against stored official-source snapshots under a named policy version. | Publication policy engine |
| `human_verified` | A real person additionally checked the cited claims. | Authenticated human reviewer |
| `insufficient_evidence` | A required claim or check is missing, contradictory, or unresolved. | Publication policy engine |

`retrieved_at` records when a source was fetched. `source_checked_at` records
when the automated gates passed. `verified_at`, `verified_by` and
`last_verified_at` remain **human-only**; an agent, extractor, scheduler, or
automatic refresh must never set them. `validation_policy_version` identifies
the gate version. `publication_assurance` is a label derived from the decision
and any genuine human review. Freshness is a separate state; a previously
source-checked record can later become stale.

These new fields belong to publication/revision metadata, not the current
`Opportunity` seed YAML or the applicant's profile. Their storage and API shape
will be implemented with the pipeline; do not add empty placeholders to all
four fixtures.

## Required gates for automatic publication

All checks below must pass. A model confidence score cannot override a failed
check.

1. **Source and access:** URL belongs to an approved government, university, or
   foundation source; its access rules permit the fetch method. Store source
   identity, URL, retrieval result, content hash, and parser version.
2. **Claim evidence:** Every material amount, currency, rate year, deadline,
   stage, intake, application route, eligibility restriction, and funding
   relationship points to a passage or table cell in a retained snapshot.
   Extracted text is compared with that snapshot. An HTTP 200 alone is not
   evidence.
3. **Structure and semantics:** The `Opportunity` schema validates. Unknown
   values remain unspecified. Amounts are not summed; tuition reduction is not
   called a stipend; no deadline year, degree recognition, or entitlement is
   inferred.
4. **Consistency:** Round, route, applicant category, deadline, and rate year
   agree. A historical amount may be shown only with its year. Conflicting
   current claims hold the candidate.
5. **Identity and change:** Duplicate candidates are reconciled. A change to a
   published material fact is supported by a fresh snapshot and recorded as an
   immutable revision with the prior value and reason.
6. **Safety of output:** The public listing names its assurance and freshness
   state. Unsupported claims do not enter the public record. A failed source
   fetch never means the scholarship closed.

## Decisions

| Decision | New candidate | Existing published record |
|---|---|---|
| `publish` | All gates pass; publish as `source_checked`. | Publish an evidenced revision; keep the previous revision. |
| `hold` | Missing or conflicting evidence; keep private and retry. | Retain last-known-good facts, flag the affected claim or record for recheck. |
| `reject` | Invalid identity, prohibited source, or persistent schema/semantic failure; record reasons. | Do not replace the published version; escalate the anomaly. |
| `stale` | No public record to preserve. | Fetch failed or freshness threshold passed; retain last-known-good facts and show a warning. |

Each decision stores policy version, checked time, snapshot IDs, passed/failed
checks, candidate/revision IDs, and machine-readable reasons. Publishing is
atomic with the revision and its validation report. Repeated processing of the
same snapshot must not create duplicate revisions.

## Operational contracts (to be designed and implemented)

| Contract | Responsibility |
|---|---|
| `Source` | Official organization, URL, permission and monitoring schedule. |
| `SourceSnapshot` | Immutable content/hash, fetch time, response status, parser version. |
| `ExtractedCandidate` | Proposed `Opportunity` plus field-level evidence references. |
| `ValidationReport` | Deterministic checks, conflicts, source and policy versions. |
| `PublicationDecision` | Publish/hold/reject/stale with reasons and assurance. |
| `OpportunityRevision` | Immutable published version and change history. |
| `SourceHealth` | Last success, failures, retries and anomalies. |

## First milestone and current fixtures

The first unattended-path demonstration re-fetches the four S01 official
sources, recognizes unchanged claims, detects a changed claim, and makes a
deterministic publish/hold/stale decision without a human click. The fixtures
remain regression inputs, not automatically trusted records.

The [first-pass review](slices/S01/FIRST-PASS-REVIEW.md) found route, rate-year,
and deadline issues. Those candidates must stay on hold until corrected and
validated against snapshots. Routine operation must not depend on a human
reviewing every update; exceptional conflicts may be escalated to a person.

Track automatic-publication rate, unsupported-claim incidents, source failures,
duplicate rate, stale-record count, and time from source change to safe revision.
Set numeric targets only after a baseline exists.
