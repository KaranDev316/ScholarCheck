# Publication policy — autonomous, evidence-first

Status: **policy `s01.publication.3` implemented; local publication and
monitoring acceptance tests complete (5 November 2026).** CGRS D has a retained
proposal, separate source-context adjudications and a passing report in
`content/publication/cgrs-d/complete-run/`. It has been published in disposable
PostgreSQL. RMIT remains held. Production deployment and live model-provider
execution are still outstanding; see `DEPLOYMENT.md`.

The implementation below supersedes the historical `.1` and `.2` gate notes.
Currency, units, rate years and routes now have conservative value checks;
amounts use decimal parsing with token boundaries, and source rows must associate
amount, currency, period and any stated rate year. Unsupported or ambiguous
formats hold rather than receive a guessed interpretation. Public prose,
programme details and round labels also require material-fact coverage.
Reports bind the candidate content hash, fact-table fingerprint and full snapshot
fingerprints (including source identity, text, retrieval time, status and parser).
Every stated reading requires its own supported verdict; conflicts always hold.

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

The pipeline uses one AI pass to extract candidate facts and a separate
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

## Implemented publication path

`publication/pipeline.py` runs extraction and checking separately, retains their
raw and validated outputs, then evaluates the gate. It accepts configured
commands or the built-in `model_pass.py` adapter. Models cannot publish. An
incomplete response, invalid output or refusal cannot become a supported claim.
The committed launch inputs came from the Codex source review, not a live
Responses API invocation; transport behavior is tested with injected responses.

`candidate.py` validates proposals against retained spans and derives fact
states. `evidence_check.py` requires one adjudication per stated reading; multiple
readings on a page must identify evidence and excerpt explicitly. `gates.py`
checks required facts, snapshot binding, excerpt presence, values and associated
qualifiers, applicability, conflict states, official action hosts and open review
findings. The gate also checks that public fields agree with the fact table.

`store.publish` loads the findings register itself, locks publication of the
record, evaluates the gate and atomically stores snapshots, facts, report,
immutable revision and assurance. Identical candidate/report/snapshot processing
reuses the revision and its original check timestamp. A changed report or
snapshot set remains auditable as a new revision. SQL triggers prohibit changes
to retained snapshots, published revisions and revision-to-snapshot links.

`models/public.py` is an explicit public allowlist. The APIs read only the
published revision, including in development; neither held candidates nor mutable
seed data can appear through them. Funding labels derive from supported coverage
facts. Full tuition requires explicit full coverage, living support a supported
living-cost fact, and flights an explicit flight benefit. Partial tuition or a
relocation allowance cannot produce a full-coverage category. Unknown-year dates
are displayed without inferring that applications are open.

`api/opportunities.py` implements published list/search/filter/detail and
protected problem-report ingestion. Internal passages, snapshot references,
reports, policy version, revision IDs and caller hashes are omitted. Source-check
dates and official links remain public.

## Operational state and monitoring

The published revision's linked official URLs form the one-record monitor's
source registry. `monitor_state` stores due times, failure counts and the last
observed hashes; `monitor_runs` records each attempted outcome. Retained files
keep collection provenance. The worker checks the approved host before each
redirect fetch and follows the source's access rules.

Unchanged source text invokes neither AI pass and creates no revision. Changed
text runs the same pipeline, or is held if model configuration is absent. A
failed fetch or uncertain check preserves the last supported revision and its
check timestamp, records stale/recheck state, and schedules a retry. Test
coverage includes a material amount change held on unsupported evidence and then
published on a supported check, without modifying the prior revision.

The launch milestone is proven locally with CGRS D. Production release still
requires a real contact address, hosting origin and a smoke test at that origin.
See `DEPLOYMENT.md` for configuration, publication replay and monitoring commands.
