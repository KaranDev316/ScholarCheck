# S01 verification — Foundation and public MVP

Rebased 23 October 2026 under D-09 and D-10. The former personal assessment
scenarios AC-01..AC-14 remain deferred. S01 now includes initial publication
and a public catalogue, while scheduled monitoring follows in Stage 2.

## Scope

S01 provides the shared domain, four regression fixtures, PostgreSQL storage,
publication gates, and a public browse/search/detail experience. It proves
that every published record has source-backed assurance without claiming
human verification. A2 means **source-backed gate eligibility**, not mandatory
human approval. The four fixtures are inputs to the gate, not pre-approved
records.

## Acceptance scenarios

| ID | Scenario | Evidence required |
|---|---|---|
| F-01 | Each fixture parses as an `Opportunity`; ids and evidence references resolve; unknown values remain unspecified | Seed tests |
| F-02 | Loader stores and reads a fixture without merging `retrieved_at`, `source_checked_at` and optional human `verified_at` | Loader/API tests |
| F-03 | Unknown opportunity id returns the agreed structured not-found response | API test |
| F-04 | Source-check contract records source/snapshot ids, policy version, per-check results, decision reason and assurance; human fields can only be set by a human workflow | Contract schema and tests |
| F-05 | Known issues in `FIRST-PASS-REVIEW.md` are represented as failed/uncertain checks and cannot be labelled `source_checked` | Fixture audit tests/report |
| F-06 | Read responses expose assurance and freshness honestly; an unreviewed YAML record never says “human verified” or “source checked” solely because it parsed | API tests |
| F-07 | A source failure is represented as unavailable/needs recheck in the contract; it never implies a round closed | Contract tests |
| F-08 | Each of four records passes all publication gates against retained official-source snapshots; known first-pass issues are resolved or the affected record stays held | Validation reports, snapshot references and publication tests |
| F-09 | Public APIs expose only published records and support search plus country, study level and funding filters | API tests including unpublished/empty/unknown cases |
| F-10 | A visitor can browse, filter, inspect stated eligibility, deadlines and evidence, open official links, and share a stable direct URL without an account | UI tests and deployed smoke check |

F-01..F-07 retain the earlier foundation proof. F-08 requires real retained
source content for initial publication. Scheduled re-fetch and unattended
change handling are Stage 2 work. Passing seed parsing alone never grants
publication assurance.

## Invariants

1. Four eligibility outcome values only; no probability or match percentage.
2. Unresolved degree recognition stays unknown; grades retain original scale.
3. Funding components remain separate; tuition reduction is not a stipend.
4. Route, intake, rate year and stage remain distinct; absent facts are unknown.
5. Retrieval, automated source check and human verification are separate events.
   Agents and workers never set human verification fields.
6. Every material published claim must pass
   `PUBLICATION-POLICY.md`; an HTTP response or schema pass alone is inadequate.
7. A failed fetch retains prior facts and signals recheck; it never marks a
   scholarship closed.
8. Personal profile data is not persisted server-side.

## Interfaces and gates

The existing personal assessment proposal in `PROPOSED-CONTRACTS.md` is
deferred, except that the error envelope can be reused. Define machine
assurance and publication decision schemas separately from the YAML fixtures.
`PUBLICATION-POLICY.md` is the policy source of truth.

## Definition of done

F-01..F-10 have tests or recorded proof, all four records pass the gates and
are public, and the no-account site works at a deployed URL. `EVIDENCE.md`
maps proof to each criterion. No human approval is required; failed gates
still block publication.
