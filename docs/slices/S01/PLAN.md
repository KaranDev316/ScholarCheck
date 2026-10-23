# S01 plan — Foundation for autonomous publication

Rebased 23 October 2026 under D-09. Read `CONTEXT.md`,
`PUBLICATION-POLICY.md`, `ROADMAP.md` and `VERIFICATION.md` before work.
The old profile/listing/save implementation steps are now S07 work; the
existing scaffold is retained. Do not treat a schema pass or a successful HTTP
fetch as permission to publish.

## Completed

1. T01-T02: FastAPI/React scaffold, domain types, health endpoint and tests.
2. T03: four unverified YAML regression fixtures and structural tests.
3. Agent first-pass source comparison in `FIRST-PASS-REVIEW.md`. Its findings
   require correction or a hold decision; it did not set human verification.

## Remaining sequence

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
- Handoff to S02 with four source URLs and known expected differences.

## Boundaries

S01 defines the data and policy contracts; S02 re-fetches official sources,
S03 extracts candidates, S04 validates and publishes automatically, and S07
builds the student journey. The proposed assessment API in
`PROPOSED-CONTRACTS.md` remains a review draft for S07 and does not block
T04-T06. Current human-only verification fields remain optional.

No automatic publication is enabled merely by completing this plan.
