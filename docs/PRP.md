# PRP.md — Product requirements

Depends on `CONTEXT.md` decisions D-09 and D-10 and
`PUBLICATION-POLICY.md`. `ROADMAP.md` defines delivery order.

## Product and audience

ScholarCheck helps prospective bachelor's, master's and doctoral applicants
find scholarships and inspect what official sources actually say about
eligibility, funding, deadlines and applications. The first release contains
four existing scholarships and is accessible without an account.

## First-release requirements (Stage 1)

| ID | Requirement | Acceptance |
|---|---|---|
| MVP-01 | Public catalogue | A visitor can browse the four published scholarships without signing in; unpublished fixtures never appear |
| MVP-02 | Search and filters | Search scholarships and filter by destination country, study level and funding; active filters and an empty state are clear |
| MVP-03 | Scholarship detail | Each direct URL shows scheme, programme/round, stated eligibility, funding components, deadlines, source evidence, assurance and freshness |
| MVP-04 | Official actions | Requirements/source and application links are distinct, labelled and point to official destinations; an unavailable application route is stated clearly |
| MVP-05 | Sharing | A visitor can copy or share a stable scholarship URL that opens the same public detail page |
| MVP-06 | Evidence-backed publication | Material public claims pass the gates in `PUBLICATION-POLICY.md` against retained official-source content; contradictions or missing evidence hold the record |
| MVP-07 | Honest unknowns | Unspecified amounts, dates, eligibility and application status remain unknown; funding components are not summed or relabelled |
| MVP-08 | Public quality | Keyboard access, readable mobile layout, clear errors and loading states, and no assurance claim beyond the stored decision |

The four existing YAML fixtures are starting candidates and regression inputs.
Their first-pass review identified issues that must be corrected or held. A
successful HTTP response or schema check alone cannot publish them.

## Reliable update requirements (Stage 2)

| ID | Requirement | Acceptance |
|---|---|---|
| MON-01 | Register one official source | Its identity, permitted fetch method, URL and schedule are recorded |
| MON-02 | Fetch and compare | Immutable snapshots and hashes distinguish unchanged, changed and failed fetches; unchanged content does not create another revision |
| MON-03 | Validate meaningful changes | Each changed material claim is traced to the new snapshot and runs through the same publication gates as Stage 1 |
| MON-04 | Safe decision | Supported changes publish an atomic revision; uncertainty holds with reasons; fetch failure retains the last-known-good record and signals recheck |
| MON-05 | Unattended operation | Scheduling, retries, idempotency and a decision trail demonstrate a change can be updated or held without owner action |

Extend monitoring to the other three records after MON-01..05 pass on one.

## Growth requirements (Stage 3)

Discover official opportunities, extract candidates with field-level evidence,
reconcile identity and duplicates, and publish through the established gates.
The first two stages do not depend on automatic discovery.

## Later student features

Personal profiles and requirement-by-requirement fit assessments, local saved
items, comparison, checklists, reminders and account sync are deferred. The
first release shows source-stated eligibility and does not imply a personal
eligibility decision or probability of award.

## Shared constraints

- Human verification is optional and separately attributed; automated source
  checking never sets human verification fields.
- Published records keep source links, evidence, policy version and revision
  history. Unknowns remain visible as unknowns.
- A failed fetch or passed deadline never silently deletes or closes another
  valid round.
- No personal applicant data is needed for the first release.
- Automatic application submission, match scores, copying competitor content
  and private-source scraping are out of scope.

## Release gates

**Stage 1:** Four records pass the publication policy, the public MVP journeys
work at a deployed URL, and the API/UI expose only published records. If any
record is held, Stage 1 is incomplete and the reason is reported.

**Stage 2:** One published record is monitored unattended. Tests demonstrate
unchanged, safe change, conflicting change and fetch-failure paths, including
revision and last-known-good behaviour.
