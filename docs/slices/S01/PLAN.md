# S01 plan — Public four-scholarship MVP

Rebased 23 October 2026 under D-09 and D-10. Read `CONTEXT.md`,
`PUBLICATION-POLICY.md`, `ROADMAP.md` and `VERIFICATION.md` before work.
The profile/assessment/save steps are deferred; public catalogue and detail
are part of this slice. Do not treat a schema pass or a successful HTTP fetch
as permission to publish.

## Completed

1. T01-T02: FastAPI/React scaffold, domain types, health endpoint and tests.
2. T03: four unverified YAML regression fixtures and structural tests.
3. Agent first-pass source comparison in `FIRST-PASS-REVIEW.md`. Its findings
   require correction or a hold decision; it did not set human verification.

## Delivery sequence

### Step 1 — Read model and storage (T04-T05; implemented, proof in EVIDENCE)

- Define PostgreSQL tables for opportunities, programmes, rounds, rules,
  components and evidence with stable ids. Keep seed import repeatable.
- Define `GET /api/v1/opportunities/{id}` with a structured 404. Return the
  current facts and their actual assurance state; no default “verified” label.
- Test repeated loads, read/not-found, field fidelity, and separation of
  retrieved versus human-verified timestamps.
- Record the read response and error example in `EVIDENCE.md`.

### Step 2 — Operational contracts (T06)

- Define `Source`, `SourceSnapshot`, `ExtractedCandidate`,
  `ValidationReport`, `PublicationDecision`, `OpportunityRevision` and
  `SourceHealth` as versioned contracts. Keep them separate from the YAML
  `Opportunity` format.
- Include `source_checked_at`, `validation_policy_version`,
  `publication_assurance` and optional human verification with distinct
  meanings. A machine decision must not assign a human name/time.
- Specify publish/hold/reject/stale reasons and retained snapshot references.
  Test serialization and invalid states. No scheduler or live publisher yet.

### Step 3 — Fixture audit baseline (T07)

- Turn the known discrepancies in `FIRST-PASS-REVIEW.md` into machine-readable
  expected holds, including CGRS route, RMIT rate/part-time wording, and passed
  RMIT/Sydney round deadlines. Correct fixture claims when sources support the
  correction; keep unknowns explicit.
- Test that a fixture with a known material conflict cannot claim
  `source_checked`. Test that a failed fetch retains prior facts in the
  operational decision contract.
- Do not set `verified_at`, `verified_by` or `last_verified_at`.

### Step 4 — S01 proof (T08)

- Run backend tests and relevant frontend scaffold checks.
- Map F-01..F-07 from `VERIFICATION.md` to tests, API examples and hold
  reports in `EVIDENCE.md`. Mark any criterion unproven honestly.
- Carry the four source URLs and known expected differences into publication
  tests and the later S02 monitoring handoff.

### Step 5 — Resolve and publish the four records (T09-T10)

- Correct the fixture route, rate-year, deadline and wording issues from
  `FIRST-PASS-REVIEW.md`. Obtain retained official-source snapshots and map
  every material displayed claim to a passage or table cell.
- Implement the publication policy gates, decision report, immutable revision
  and atomic publish/hold operation. Keep human verification fields human-only.
- Publish each of the four records only after its own gate passes. Record
  specific hold reasons for any candidate that cannot pass.

### Step 6 — Public website (T11-T12)

- Add published-only catalogue/search/filter endpoints for country, study
  level and funding. Detail responses expose stated eligibility, funding,
  deadlines, evidence, assurance, freshness and distinct official links.
- Build browse/search/filter and shareable detail pages without an account.
  Include empty, loading, error and mobile states and keyboard access.
- Run backend/frontend tests and a deployed end-to-end smoke check for all
  first-release journeys; record proof in `EVIDENCE.md`.

## Boundaries

S01 now includes initial source-backed publication and the public MVP. S02
monitors one published scholarship and proves safe unattended update/hold;
S03 adds discovery and growth. The proposed personal assessment API in
`PROPOSED-CONTRACTS.md` remains a later-work draft. Current human-only
verification fields remain optional. Completing a contract alone does not
enable publication; an individual record must pass the implemented gates.
