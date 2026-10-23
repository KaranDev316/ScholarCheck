# PRP.md — Product Requirements

Depends on `CONTEXT.md`, especially D-09, and
`PUBLICATION-POLICY.md`. Priorities below describe the eventual product;
`ROADMAP.md` sequences pipeline work before the full student experience.

## 1. Product overview
An autonomous scholarship discovery and monitoring platform that continuously
collects, validates and updates opportunities from official sources. Students
see the evidence and assurance behind each important claim while judging
whether a funded bachelor's, master's or doctoral opportunity fits.

## 2. Users, problem, primary journey
- **User:** International student seeking a funded degree at bachelor's, master's or doctoral level; persona P1: Malawian national, living in India, three-year BCA, limited funds.
- **Problem:** Listings overstate funding, hide blockers and collapse deadlines, forcing manual interpretation.
- **Student journey:** Find a source-checked opportunity → inspect eligibility,
  funding, deadlines, evidence and freshness → save a next action.
- **Operating journey:** Register an official source → fetch and retain a
  snapshot → extract a candidate → run independent gates → publish a revision
  automatically or hold it with reasons → monitor for changes and failures.

## 3. Autonomous publication requirements

| ID | Requirement | Success | Failure behaviour | Pri |
|---|---|---|---|---|
| SYS-01 | Register official sources with identity, access rules and monitoring cadence | Only permitted sources enter the pipeline | Disallowed or inaccessible source is held |
| SYS-02 | Fetch and retain immutable source snapshots with hash and parser version | Every published claim can be traced to the content checked | Fetch failure retains last-known-good record |
| SYS-03 | Extract candidate opportunity facts with field-level evidence | Candidate preserves amounts, dates, routes, rate years and unknowns | Unsupported values stay unknown |
| SYS-04 | Validate source, evidence, schema, semantics, round/funding consistency, identity and changes | All gates pass before automatic publication | Conflict or missing material evidence holds or rejects candidate |
| SYS-05 | Publish immutable revisions and assurance metadata automatically | Safe changes appear without a human approval click | Failure leaves the previous revision intact |
| SYS-06 | Monitor and retry sources; surface stale state and anomalies | Source failures do not silently erase or close opportunities | Persistent failures raise an operational alert |
| SYS-07 | Discover new official opportunities and reconcile duplicates | Catalogue grows without routine editorial work | Duplicates are merged or held for resolution |
| SYS-08 | Measure automatic publication, unsupported claims, source failures, duplicates and staleness | Autonomy and quality can be audited | Missing telemetry is visible |

## 4. Student-facing requirements
| ID | Requirement | Actor / trigger | Success outcome | Essential failure behaviour | Pri |
|---|---|---|---|---|---|
| REQ-01 | User can enter a profile (nationality, residence country, degree type, degree duration, degree status, intended level, optional grade with original scale) | Student opens tool | Profile held in the browser and used for assessments | Invalid/missing required fields are flagged; nothing is guessed | Must |
| REQ-02 | User can open an opportunity and see a structured listing (scheme, programme, round, funder, official links) | Student selects a listing | Listing shows decision information first and links to official requirements and application portal as distinct actions | Unknown opportunity shows a not-found message with a way back | Must |
| REQ-03 | User can see a requirement-by-requirement eligibility assessment with one of four outcomes and reasons | Student opens listing with a profile | Each rule shows result, reason and evidence; overall outcome follows domain rules | No profile → prompted to enter one, rules still listed; unresolved rule never becomes "met" | Must |
| REQ-04 | User can see funding broken down by component with duration, currency and conditions | Student opens listing | Components shown separately with "unspecified" where unknown; no summed total | Missing component shows "Unspecified", never zero or full | Must |
| REQ-05 | User can see every deadline by stage, applicant category and round, with status | Student opens listing | Deadlines labelled; closing one round leaves others open; date-only stays date-only | Unannounced/rolling/closed/needs-recheck states displayed explicitly | Must |
| REQ-06 | User can view the evidence behind each important claim | Student selects "evidence" | Source link, supporting passage, retrieved-at, source-checked-at, policy version, and optional human verification shown distinctly | Claim without evidence is withheld or labelled insufficient, never confirmed | Must |
| REQ-07 | User can browse and filter opportunities by degree level, subject, nationality eligibility, destination and funding coverage | Student opens catalogue | Filtered list with active filters visible | No results → empty state offering to clear filters | Must |
| REQ-08 | User can save an opportunity with a next action and note | Student selects Save | Saved item persists in the browser across reloads | Storage unavailable → clear message; nothing silently lost | Must |
| REQ-09 | User can compare up to three saved opportunities side by side (eligibility outcome, funding components, deadline, remaining costs) | Student selects compare | Aligned table; differences visible | Fewer than two or more than three selected → explained | Must |
| REQ-10 | User can track each saved opportunity through Saved, Checking eligibility, Preparing, Submitted, Decision recorded | Student updates status | Status stored, labelled as user-reported | Invalid transitions are not offered | Should |
| REQ-11 | User can keep a per-opportunity checklist derived from requirements | Student opens saved item | Checklist items tick off and persist | Opportunity changed since saved → student is told what changed | Should |
| REQ-12 | User can see source-check time, assurance and freshness, with a visible warning when overdue or source-unavailable | Student opens listing | Automated and optional human verification are labelled separately | Previous data retained, never blanked | Must |
| REQ-13 | Maintainer can inspect decisions, correct exceptional cases and optionally human-verify claims | Maintainer signs in | Override and human actions are attributed and logged | Routine publication does not wait for a maintainer; unevidenced claims stay held | Must |
| REQ-14 | User can sync saved items across devices via an account | Student registers | Saved state follows account | Registration failure leaves local data intact | Should (deferred) |

## 5. User flows
- **Operating happy path:** SYS-01 → SYS-02 → SYS-03 → SYS-04 → SYS-05 →
  SYS-06. Human approval is not a step.
- **Student happy path:** REQ-07 → REQ-02 → REQ-01 → REQ-03/04/05 →
  REQ-06/12 → REQ-08.
- **Failure journeys:** (a) student's degree recognition is unresolved → "Potential fit, confirmation needed"; (b) award requires enrolment in an eligible Canadian doctoral programme → blocker visible at top; (c) source page unreachable → previous data with recheck warning; (d) saved opportunity's round closes → status updated, other rounds unaffected.

## 6. Nonfunctional requirements
- **Privacy:** no personal profile data stored server-side in MVP; no tracking beyond what is disclosed.
- **Accessibility:** keyboard operable; outcomes not conveyed by colour alone; target WCAG level TBD.
- **Data integrity:** domain rules 1-9 in CONTEXT.md and every gate in
  `PUBLICATION-POLICY.md` are binding. AI extraction may propose, never
  authorize, a claim.
- **Reliability / performance targets:** TBD (no invented numbers).
- **Security:** internal tool requires authentication; input validated server-side.

## 7. Out of scope
Community, document upload, automatic **application** submission,
probability/match scores, native app, worldwide coverage, publishing solely on
AI confidence, copying competitor content, REQ-14 (deferred).

## 8. Dependencies, risks, open questions
- **Content accuracy** remains the main risk. The validation gates are a release
  dependency, not a later quality enhancement.
- The four S01 fixtures are regression benchmarks. Their first-pass review
  found issues; none gains `source_checked` assurance just because the YAML
  parses or its URLs respond.
- Source access permissions, HTML/PDF variability, and changing application
  routes are operating risks. Use conservative holds and last-known-good data.
- Open: destinations, product name, hosting, accounts, source registry policy.

## 9. Release criteria
1. First pipeline milestone: re-fetch four benchmark sources, detect unchanged
   and changed material facts, and produce deterministic publish/hold/stale
   decisions without human approval. No unresolved fixture issue is published.
2. Product release: 20-30 `source_checked` records across the chosen levels
   and destinations, each with retained snapshots, field-level evidence,
   policy version, revision history and visible freshness.
3. All required gates and student Must requirements demonstrated, including
   source failure, contradiction, duplicate and rollback cases.
4. Usability check with 5-8 users, plus measured automatic-publication rate,
   unsupported-claim incidents, source failures, duplicates and stale records.

## 10. Requirement-to-source notes
REQ-01..06, 08, 12: audit "first vertical slice" and acceptance criteria. REQ-07: priority 2. REQ-09: priority 4. REQ-10/11: priority 5. REQ-12 and REQ-13: priority 7 and quality rule. REQ-14: audit "account when saving across devices" (assumed deferred, D-05).
SYS-01..08 and revised REQ-06/12/13 follow owner direction D-09.
