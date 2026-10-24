# S01 verification — Foundation and public MVP

Rebased 24 October 2026 under D-09..D-11. The former personal assessment
scenarios AC-01..AC-14 remain deferred. S01 now includes initial publication
and a public catalogue, while scheduled monitoring follows in Stage 2.

## Scope

S01 provides the shared domain, four regression fixtures, PostgreSQL storage,
publication gates, and a public browse/search/detail experience. It proves
that every published record has automated source-backed assurance. The four
fixtures are regression inputs, not a required launch set.

## Acceptance scenarios

| ID | Scenario | Evidence required |
|---|---|---|
| F-01 | Each fixture parses as an `Opportunity`; ids and evidence references resolve; unknown values remain unspecified | Seed tests |
| F-02 | Loader stores and reads a fixture with retrieval and automated source-check timestamps distinct; legacy human fields are migrated out | Loader/API and migration tests |
| F-03 | Unknown opportunity id returns the agreed structured not-found response | API test |
| F-04 | Source-check contract records source/snapshot ids, policy version, per-check results, fact states, decision reason and assurance; no human-verification state exists | Contract schema and tests |
| F-05 | Known issues in `FIRST-PASS-REVIEW.md` are represented as failed/uncertain checks and cannot be labelled `source_checked` | Fixture audit tests/report |
| F-06 | Read responses expose assurance and checked date honestly; a YAML fixture never says “source checked” solely because it parsed | API tests |
| F-07 | A source failure is represented as unavailable/needs recheck in the contract; it never implies a round closed | Contract tests |
| F-08 | Every launch record passes separate AI evidence checking plus provider, exact-evidence, value/context, conflict and funding-coverage code gates against retained snapshots; unsupported or unclear candidates stay held | Validation reports, snapshot references and publication tests |
| F-09 | Public APIs expose only published records and support search plus country, study level and the three funding-type filters | API tests including unpublished/empty/unknown cases |
| F-10 | A visitor can browse, filter, inspect stated eligibility, deadlines and exact evidence, open confirmed official links, and share a stable URL without an account | UI tests and deployed smoke check |
| F-11 | “Fully funded” appears only with explicit tuition, living and flights evidence; amount basis and partial exemptions remain accurate | Classification tests and UI check |
| F-12 | Problem reports reach a protected endpoint and real branding/contact details replace placeholders | API/UI and deployed smoke check |

F-01..F-07 retain the earlier foundation proof. F-08 requires real retained
source content for initial publication. Scheduled re-fetch and unattended
change handling are Stage 2 work. Passing seed parsing alone never grants
publication assurance.

## Invariants

1. Four eligibility outcome values only; no probability or match percentage.
2. Unresolved degree recognition stays unknown; grades retain original scale.
3. Funding components remain separate; tuition reduction is not a stipend.
4. Route, intake, rate year and stage remain distinct; absent facts are unknown.
5. Retrieval and automated source check are separate events. Legacy human
   verification fields are removed from active contracts.
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

F-01..F-12 have tests or recorded proof, every chosen launch record passes the
gates, and the no-account site works at a deployed URL. `EVIDENCE.md` maps
proof to each criterion. Failed gates block publication regardless of count.
