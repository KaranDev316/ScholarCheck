# Publication policy — autonomous, evidence-first

Status: **product direction updated 24 October 2026; implementation pending**.
All publication decisions are automated. No human verification or
human-verification UI is part of ScholarCheck. This does not declare the
current YAML fixtures publishable. The existing code still contains legacy
human-verification fields; removing them is migration work, not completed by
this document.

## Assurance and timestamps

| Label | Meaning | Who may set it |
|---|---|---|
| `source_checked` | Every required automated gate passed against stored official-source snapshots under a named policy version. | Publication policy engine |
| `insufficient_evidence` | A required claim or check is missing, contradictory, or unresolved. | Publication policy engine |

`retrieved_at` records when a source was fetched. `source_checked_at` records
when the automated gates passed. `validation_policy_version` identifies the
gate version. `publication_assurance` is derived from that decision alone.
Legacy `verified_at`, `verified_by`, `last_verified_at` and `human_verified`
must be removed from the active data/API contract, with a deliberate database
and fixture migration. The public UI uses the actual check date and a plain
source-match result; policy version and revision metadata remain internal.
Freshness is separate from assurance.

Publication fields belong to revision metadata, not applicant data. Each
material extracted fact has a first-class state: `stated`, `unspecified` or
`conflicting`, plus an evidence reference when stated. Do not use a bare null
to hide uncertainty. A conflicting or missing material fact holds the
candidate; it cannot be converted to a positive public claim.

## Required gates for automatic publication

All checks below must pass. A model confidence score cannot override a failed
check.

1. **Source and access:** URL belongs to a government body or an established,
   well-known institution on the approved provider list; its access rules
   permit the fetch method. Store source
   identity, URL, retrieval result, content hash, and parser version.
2. **Claim evidence:** Every material amount, currency, rate year, deadline,
   stage, intake, application route, eligibility restriction, and funding
   relationship points to a passage or table cell in a retained snapshot.
   Exact displayed excerpts must occur in that saved snapshot; values and
   units must agree with the cited wording or table cell. An HTTP 200 alone
   is not evidence. A model may propose facts but cannot publish them.
3. **Structure and semantics:** The `Opportunity` schema validates. Unknown
   values remain unspecified. Amounts are not summed or converted; tuition
   reduction is not called a stipend; no deadline year, degree recognition,
   entitlement, or coverage category is inferred.
4. **Consistency:** Round, route, applicant category, deadline, and rate year
   agree. A historical amount may be shown only with its year. Conflicting
   current claims hold the candidate.
5. **Identity and change:** Duplicate candidates are reconciled. A change to a
   published material fact is supported by a fresh snapshot and recorded as an
   immutable revision with the prior value and reason.
6. **Funding classification:** Compute “Fully funded” only when retained
   official evidence explicitly supports tuition, living costs **and flights**
   coverage. Compute “Tuition + stipend” and “Tuition” from evidenced
   components. If no category is supported, leave it untagged. A partial
   exemption must not become full tuition coverage. Recompute and withdraw
   labels on every supported revision.
7. **Safety of output:** Public pages show the actual check date and a plain
   source-match result, with exact evidence accessible. Internal claim counts,
   policy version and revision IDs stay out of the UI. Unsupported claims do
   not enter the public record. A failed fetch never means the scholarship
   closed; a passed date marks only its own round as “Date passed.”

## Decisions

| Decision | New candidate | Existing published record |
|---|---|---|
| `publish` | All gates pass; publish as `source_checked`. | Publish an evidenced revision; keep the previous revision. |
| `hold` | Missing or conflicting evidence; keep private and retry. | Retain last-known-good facts, flag the affected claim or record for recheck. |
| `reject` | Invalid identity, prohibited source, or persistent schema/semantic failure; record reasons. | Do not replace the published version; record the anomaly. |
| `stale` | No public record to preserve. | Fetch failed or freshness threshold passed; retain the last supported facts and check date; record an internal warning. |

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

## First publication and monitoring milestone

Stage 1 validates a small launch set for a public website. The four existing
fixtures are candidates, subject to audit and the open launch-set decision.
Their source-backed publication decisions use the gates above and retained
official-source content. Scheduled re-fetch is a separate Stage 2
capability: start with one published scholarship, then prove that an unchanged
page does no work and that a meaningful change is updated or held safely
without owner intervention. The fixtures remain regression inputs, not
automatically trusted records.

The [first-pass review](slices/S01/FIRST-PASS-REVIEW.md) found route, rate-year,
and deadline issues. Those candidates stay on hold until corrected and
validated against snapshots. Unresolved conflicts remain held automatically.

Track automatic-publication rate, unsupported-claim incidents, source failures,
duplicate rate, stale-record count, and time from source change to safe revision.
Set numeric targets only after a baseline exists.
