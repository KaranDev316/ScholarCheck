# S01 verification — Foundation and honest evidence

Rebased 23 October 2026 under D-09. The former “one complete decision” UI
acceptance scenarios AC-01..AC-14 move to S07 and are not S01 exit criteria.
Their historical notes remain in `EVIDENCE.md` for traceability. S01 does not
publish automatically; S04 implements that engine.

## Scope

S01 provides the shared domain, four regression fixtures, PostgreSQL storage,
an opportunity read endpoint, and explicit source-check/publication contracts.
It proves that data can be read without falsely claiming human or automated
assurance. A2 now means **source-backed gate eligibility**, not mandatory human
approval. The four current fixtures are inputs to the gate, not pre-approved
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

The S01 contract may use deterministic fixture checks or a stubbed snapshot.
Live re-fetch, extraction and publication are S02-S04 work. Passing S01 never
grants automatic publication assurance to the seed files.

## Invariants

1. Four eligibility outcome values only; no probability or match percentage.
2. Unresolved degree recognition stays unknown; grades retain original scale.
3. Funding components remain separate; tuition reduction is not a stipend.
4. Route, intake, rate year and stage remain distinct; absent facts are unknown.
5. Retrieval, automated source check and human verification are separate events.
   Agents and workers never set human verification fields.
6. Every material published claim must eventually pass
   `PUBLICATION-POLICY.md`; an HTTP response or schema pass alone is inadequate.
7. A failed fetch retains prior facts and signals recheck; it never marks a
   scholarship closed.
8. Personal profile data is not persisted server-side.

## Interfaces and gates

The existing assessment/error proposal in `PROPOSED-CONTRACTS.md` is deferred
to S07, except that the error envelope can be reused for the S01 read endpoint.
Before T05, record the read response and 404 shape. Before T06, define the
machine assurance and publication decision schemas in a separate operational
contract; do not add publication fields to all `Opportunity` YAML files merely
as placeholders. `PUBLICATION-POLICY.md` is the policy source of truth.

## Definition of done

F-01..F-07 have real tests or recorded contract examples; backend suite passes;
the fixture audit identifies holds for current route/rate/deadline issues;
`EVIDENCE.md` maps proof to each F criterion. No human approval is required.
No fixture is called publishable until the S04 gates run and pass.
