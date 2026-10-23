# PRP.md — Product Requirements

Depends on `CONTEXT.md` (decisions D-01..D-07 assumed). Priorities: **Must** = needed to prove the core advantage; **Should** = valuable, deferrable.

## 1. Product overview
A scholarship decision tool that tells an international student, with checkable evidence, whether a funded bachelor's, master's or doctoral (PhD) opportunity fits their profile, what the funding really covers, which deadline applies, and what to do next.

## 2. Users, problem, primary journey
- **User:** International student seeking a funded degree at bachelor's, master's or doctoral level; persona P1: Malawian national, living in India, three-year BCA, limited funds.
- **Problem:** Listings overstate funding, hide blockers and collapse deadlines, forcing manual interpretation.
- **Main use case:** Enter profile → see matching opportunities → open one → read eligibility assessment and funding breakdown → check official evidence → save a next action.

## 3. MVP requirements
| ID | Requirement | Actor / trigger | Success outcome | Essential failure behaviour | Pri |
|---|---|---|---|---|---|
| REQ-01 | User can enter a profile (nationality, residence country, degree type, degree duration, degree status, intended level, optional grade with original scale) | Student opens tool | Profile held in the browser and used for assessments | Invalid/missing required fields are flagged; nothing is guessed | Must |
| REQ-02 | User can open an opportunity and see a structured listing (scheme, programme, round, funder, official links) | Student selects a listing | Listing shows decision information first and links to official requirements and application portal as distinct actions | Unknown opportunity shows a not-found message with a way back | Must |
| REQ-03 | User can see a requirement-by-requirement eligibility assessment with one of four outcomes and reasons | Student opens listing with a profile | Each rule shows result, reason and evidence; overall outcome follows domain rules | No profile → prompted to enter one, rules still listed; unresolved rule never becomes "met" | Must |
| REQ-04 | User can see funding broken down by component with duration, currency and conditions | Student opens listing | Components shown separately with "unspecified" where unknown; no summed total | Missing component shows "Unspecified", never zero or full | Must |
| REQ-05 | User can see every deadline by stage, applicant category and round, with status | Student opens listing | Deadlines labelled; closing one round leaves others open; date-only stays date-only | Unannounced/rolling/closed/needs-recheck states displayed explicitly | Must |
| REQ-06 | User can view the evidence behind each important claim | Student selects "evidence" | Source link, supporting passage, retrieved-at and verified-at (distinct) shown | Claim without evidence is shown as unverified and cannot claim "confirmed" | Must |
| REQ-07 | User can browse and filter opportunities by degree level, subject, nationality eligibility, destination and funding coverage | Student opens catalogue | Filtered list with active filters visible | No results → empty state offering to clear filters | Must |
| REQ-08 | User can save an opportunity with a next action and note | Student selects Save | Saved item persists in the browser across reloads | Storage unavailable → clear message; nothing silently lost | Must |
| REQ-09 | User can compare up to three saved opportunities side by side (eligibility outcome, funding components, deadline, remaining costs) | Student selects compare | Aligned table; differences visible | Fewer than two or more than three selected → explained | Must |
| REQ-10 | User can track each saved opportunity through Saved, Checking eligibility, Preparing, Submitted, Decision recorded | Student updates status | Status stored, labelled as user-reported | Invalid transitions are not offered | Should |
| REQ-11 | User can keep a per-opportunity checklist derived from requirements | Student opens saved item | Checklist items tick off and persist | Opportunity changed since saved → student is told what changed | Should |
| REQ-12 | User can see when a listing was last verified and a visible warning when it is overdue or its source was unavailable | Student opens listing | Verification date and warning shown | Previous data retained, never blanked | Must |
| REQ-13 | Maintainer can create, review, verify and correct listings, evidence and change records via an internal tool | Maintainer signs in | Changes recorded with verifier and date; substantive changes logged | Contradictory or unevidenced claims block publication | Must |
| REQ-14 | User can sync saved items across devices via an account | Student registers | Saved state follows account | Registration failure leaves local data intact | Should (deferred) |

## 4. User flows
- **Happy path:** REQ-01 → REQ-07 → REQ-02 → REQ-03/04/05 → REQ-06 → REQ-08.
- **Failure journeys:** (a) student's degree recognition is unresolved → "Potential fit, confirmation needed"; (b) award requires enrolment in an eligible Canadian doctoral programme → blocker visible at top; (c) source page unreachable → previous data with recheck warning; (d) saved opportunity's round closes → status updated, other rounds unaffected.

## 5. Nonfunctional requirements
- **Privacy:** no personal profile data stored server-side in MVP; no tracking beyond what is disclosed.
- **Accessibility:** keyboard operable; outcomes not conveyed by colour alone; target WCAG level TBD.
- **Data integrity:** domain rules 1-8 in CONTEXT.md are binding.
- **Reliability / performance targets:** TBD (no invented numbers).
- **Security:** internal tool requires authentication; input validated server-side.

## 6. Out of scope
Community, document upload, automatic submission, probability/match scores, native app, worldwide coverage, AI-generated claims published without review, copying competitor content, REQ-14 (deferred; see roadmap).

## 7. Dependencies, risks, open questions
- **Content accuracy** is the main risk: capacity estimate ≈ 20 hrs/month for 100 records twice monthly; hence 20-30 records.
- Dependency: manual research for each seeded record, with official sources reachable.
- Fixtures for S01 are drawn from the audit examples (CGRS-Doctoral, Montréal, RMIT, Sydney RTP); values must be **re-verified against official pages before release**.
- Open: destinations, product name, hosting, accounts.

## 8. MVP acceptance / release criteria
1. 20-30 verified records covering bachelor's, master's and doctoral study in 3 destinations, each with evidence.
2. All Must requirements demonstrated; domain rules never violated in tests.
3. Usability check with 5-8 users: time to a correct shortlist decision, missed blockers and misunderstood funding recorded against an existing site.
4. Overdue-record count and per-update time tracked.

## 9. Requirement-to-source notes
REQ-01..06, 08, 12: audit "first vertical slice" and acceptance criteria. REQ-07: priority 2. REQ-09: priority 4. REQ-10/11: priority 5. REQ-12 and REQ-13: priority 7 and quality rule. REQ-14: audit "account when saving across devices" (assumed deferred, D-05).
