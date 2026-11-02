# Publication policy — autonomous, evidence-first

Status: **gate implemented 31 October 2026; HTML collector and retained
snapshots 2 November 2026; AI evidence-check pass pending.** All publication
decisions are automated. No human verification or human-verification UI is part
of ScholarCheck. The four YAML fixtures are candidates, not publishable records:
RMIT is held for a recorded finding, and the other three have no validation
report yet (see `slices/S01/EVIDENCE.md` and
`content/publication/first-pass-review.json`).

## Assurance and timestamps

| Label | Meaning | Who may set it |
|---|---|---|
| `source_checked` | Every required automated gate passed against stored official-source snapshots under a named policy version. | Publication policy engine |
| `insufficient_evidence` | A required claim or check is missing, contradictory, or unresolved. | Publication policy engine |

`retrieved_at` records when a source was fetched. `source_checked_at` records
when the automated gates passed. `validation_policy_version` identifies the
gate version. `publication_assurance` is derived from that decision alone:
`backend/app/publication/store.py` writes it in the same transaction as the
revision and its report, and the database refuses `source_checked` without a
revision. The legacy `verified_at`, `verified_by`, `last_verified_at` and
`human_verified` fields are gone from the model, the fixtures and the schema;
opening a pre-gate database demotes those rows to `insufficient_evidence` with
`needs_recheck` so no old label survives. The public UI uses the actual check
date, a plain source-check result and official provider links. Claim-linked
excerpts, retained snapshots, validation reports, policy version and revision
metadata remain internal. Freshness is separate from assurance.

Publication fields belong to revision metadata, not applicant data. Each
material extracted fact has a first-class state: `stated`, `unspecified` or
`conflicting`, plus an evidence reference when stated. Do not use a bare null
to hide uncertainty. A conflicting or missing material fact holds the
candidate; it cannot be converted to a positive public claim.

## Required gates for automatic publication

All checks below must pass. A model confidence score cannot override a failed
check.

The pipeline may use one AI pass to extract candidate facts and a separate
pass to check whether each claim is supported by the retained source in its
full context. The verifier must check applicability of the quoted text to the
same scholarship, applicant category, degree level, round, rate year and
application route, and return `supported`, `unsupported` or `unclear` with a
snapshot reference. A matching quotation by itself does not establish that
the claim applies. Code independently checks exact excerpt presence,
structured values and qualifiers, source permission, consistency, and funding
classification. Any unsupported or unclear material claim holds publication.
Neither AI pass can set `source_checked` or publish a revision.

1. **Source and access:** URL belongs to a government body, university or
   established scholarship NGO on the approved provider list; its access rules
   permit the fetch method. Store source
   identity, URL, retrieval result, content hash, and parser version.
2. **Claim evidence:** Every material amount, currency, rate year, deadline,
   stage, intake, application route, eligibility restriction, and funding
   relationship points to a passage or table cell in a retained snapshot.
   Exact displayed excerpts must occur in that saved snapshot; values and
   units must agree with the cited wording or table cell. The independent
   evidence-check pass must find that the surrounding context supports the
   claim. An HTTP 200 alone is not evidence.
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
7. **Safety of output:** Public pages show the actual check date, a plain
   source-check result and official provider links. Exact excerpts, claim-level
   evidence links, retained snapshots, validation reports, claim counts, policy
   version and revision IDs stay in the backend, not the public API or UI.
   Unsupported claims do not enter the public record. A failed fetch never means the scholarship
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

## Implemented gate (31 October 2026)

`backend/app/publication/` enforces this policy in code. The HTML collector now
retains official-source snapshots, but there is no AI evidence-check pass or
scheduled worker yet. A caller supplies the snapshots and validation report to
the publication gate, and every check below runs deterministically.

| Module | Responsibility |
|---|---|
| `collect/robots.py` | Reads `robots.txt` and decides, per user agent and path, whether a page may be fetched. An unstated restriction is allowed; a stated one is obeyed. |
| `collect/extract.py` | Turns a page into the text a passage must match: scripts, styles and page chrome removed, block structure kept as line breaks, inline markup never splitting a sentence. |
| `collect/snapshot.py` | Checks access rules first, fetches once, refuses non-HTML or near-empty pages, and writes an artifact with the request URL, final URL, status, raw and retained hashes, robots decision, user agent and parser version. Ids are content-addressed. |
| `publication/contracts.py` | `SourceSnapshot` (immutable retained text), `ClaimCheck`, `ValidationReport`, `PublicationDecision`, `PublishedRevision`. No verified-by field and no assurance above `source_checked`. |
| `publication/policy.py` | `POLICY_VERSION` (`s01.publication.1`) and the approved provider hosts. |
| `publication/register.py` | Reads `content/publication/first-pass-review.json` into a `FindingsRegister`. Holds the record that names a finding and any record citing the page it was raised on. A register that cannot be read holds everything, so a missing file never reads as “nothing outstanding”. |
| `publication/gates.py` | `evaluate()` returns publish, hold or reject with reasons. It requires a report for this exact revision and policy version; a retained snapshot from an approved provider; every cited excerpt and every displayed passage still present in that snapshot; every evidence entry covered; one excerpt per claim; and every stated amount present in the passage backing it. Any open review finding holds the candidate even when the report claims support. `register` is a required keyword argument with no default. |
| `publication/store.py` | `publish()` runs the gate first and raises `PublicationBlocked` before touching the database. The findings register is loaded inside `publish()`, not accepted as an argument, so no caller can publish a held candidate by omitting the findings. A passing decision is written in one transaction: snapshots, live facts, an immutable revision with its report and snapshot references, and the `source_checked` state pointing at that revision. A failure rolls every write back, and re-publishing identical facts keeps one revision. |

Snapshots are immutable in the database (a trigger rejects update and delete),
`revision_snapshots` links each revision to the snapshots it was checked
against, and the `publication_state.revision` foreign key and check constraint
make it impossible to store `source_checked` without the revision behind it.

Clearing a hold is an edit to the register, not to the report. Remove an entry
only after the fixture is corrected and re-checked against a retained snapshot;
a report that claims support for every entry changes nothing.

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

Stage 1 validates a small launch set for a public website. Seven pages behind the
four fixtures were retained on 2 November 2026, and every passage a fixture
quotes now occurs in its snapshot. CGRS D, the UdeM exemption and the Sydney RTP
stipend carry no open finding; RMIT is held because its 2027 round can be
neither dated nor priced from the retained text. None of them can publish until
the evidence-check pass produces a report for its revision. Scheduled re-fetch
is a separate Stage 2 capability: start with one published scholarship, then
prove that an unchanged page does no work and that a meaningful change is
updated or held safely without owner intervention. The fixtures remain
regression inputs, not automatically trusted records.

The [first-pass review](slices/S01/FIRST-PASS-REVIEW.md) found route, rate-year,
and deadline issues. The 2 November collection corrected the recorded routes,
removed one transcribed date table the pages do not contain, and left the RMIT
round held. A candidate leaves hold only when the corrected claim is checked
against a retained snapshot; unresolved conflicts remain held automatically.

Track automatic-publication rate, unsupported-claim incidents, source failures,
duplicate rate, stale-record count, and time from source change to safe revision.
Set numeric targets only after a baseline exists.
