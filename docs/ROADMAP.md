# ROADMAP.md — Vertical Slices

Inputs: `CONTEXT.md`, `PRP.md`. Greenfield; no implementation yet.

## 1. Feature map and traceability
| Feature ("User can…") | REQ | Normal journey | Error journey | Slice |
|---|---|---|---|---|
| …enter a profile | 01 | Fill form, stored locally | Invalid fields flagged | S01 |
| …open a structured listing | 02 | View listing, official links | Unknown id → not found | S01 |
| …see eligibility assessment | 03 | Four outcomes with reasons | Unresolved stays unknown | S01 |
| …see funding breakdown | 04 | Components shown | Missing = Unspecified | S01 |
| …see evidence | 06 | Open evidence | Unevidenced = unverified | S01 |
| …save with next action | 08 | Save, persists | Storage unavailable message | S01 |
| …see deadlines by round | 05 | Stage/round statuses | Closed/unannounced states | S02 |
| …see verification freshness | 12 | Verified date shown | Overdue/source-down warning | S02 |
| …browse and filter | 07 | Filter catalogue | Empty state | S03 |
| …compare up to three | 09 | Aligned table | Wrong count explained | S04 |
| …track status and checklist | 10, 11 | Update state, tick items | Changed-since-saved notice | S05 |
| Maintainer manages content | 13 | Create, verify, log change | Blocked publish | S06 |
| …sync via account | 14 | Register, sync | Local data kept | Deferred |
| (release content/readiness) | all | 20-30 records, usability test | — | S07 |

All Must/Should REQs except REQ-14 map to a slice. Gate passed.

## 2. Ordered slices
**S01 — One complete decision (NEXT).**
Objective: prove the central path end to end on a small verified fixture set. Value: a student sees whether they fit, what funding covers, and the evidence, and saves a next action. REQ: 01, 02, 03, 04, 06, 08. Acceptance: unknown degree recognition stays unknown; enrolment-only award shows its blocker first; tuition exemption not labelled stipend; evidence reachable; save persists. Out: catalogue filters, round deadlines logic beyond display, compare, tracker, admin, accounts. Risks: modelling eligibility rules generically; fixture accuracy. Prereqs: D-02 confirmed, 3-4 fixture records researched. Demo: open the app as persona P1, walk four fixtures.

**S02 — Rounds, deadlines, freshness.** REQ 05, 12. Adds Round and Deadline model, stage/category/status display, intake independence, verified/retrieved dates, overdue and source-unavailable warnings. Depends on S01 data model. Risk: time-zone and date-only handling.

**S03 — Browse and filter.** REQ 07. Catalogue page, filters on level, subject, nationality, destination, funding coverage; empty state. Depends on S01-S02. Risk: filter semantics with "unknown" values (must not hide unknowns as matches or non-matches silently).

**S04 — Compare up to three.** REQ 09. Uses saved items. Depends on S01-S03.

**S05 — Tracker and checklist.** REQ 10, 11. User-reported states, derived checklist, changed-since-saved notice (needs a minimal change marker from content).

**S06 — Internal review and recheck.** REQ 13 (+ strengthens 12). Authenticated maintainer tool, evidence entry, verification stamps, change records, publish blocking on unevidenced claims. First point where auth and (optionally) a background worker are decided. Blocking decision: maintainer auth method.

**S07 — Catalogue build and usability test.** Expand to 20-30 verified records, run the 5-8 person study. Content-heavy, no new features.

## 3. NEXT slice and why
**S01.** It resolves the largest unknowns (rule model, evidence model, funding model) and gives the earliest demonstrable feedback. Everything later builds on its data model.

## 4. S01 atomic tasks
| ID | Task | Effort |
|---|---|---|
| T01 | Scaffold repo layout, backend and frontend skeletons, lint/test runners | 90 min |
| T02 | Define domain types: Opportunity, Programme, EligibilityRule, FundingComponent, Evidence (and shared enums for four outcomes) | 60 min |
| T03 | Create seed format in `/content` and 3-4 fixture records with evidence (human-verified before release) | 120 min |
| T04 | Database schema + loader for fixtures | 90 min |
| T05 | Read endpoint for one opportunity | 60 min |
| T06 | Stateless assessment evaluator (profile + opportunity → per-rule results + overall outcome) with unit tests for every domain rule | 120 min |
| T07 | Assessment endpoint with validation and error shape | 60 min |
| T08 | Profile form + local persistence | 90 min |
| T09 | Listing page: blockers first, funding components, official links, evidence panel | 120 min |
| T10 | Save-with-next-action to local storage incl. unavailable-storage handling | 60 min |
| T11 | E2E smoke test across the demo path | 60 min |
Complexity: medium overall; T06 is the highest risk.

## 5. Parallelism
After T02 freezes the types: backend (T04-T07) and frontend shell (T08) can run in parallel. The API response shape for assessment is the **coordination contract**: agree it before T07 and T09. T03 (content) can proceed alongside code.

## 6. Milestones
M1 = S01 demo (persona P1 walkthrough). M2 = S02-S04 (deadlines, filter, compare) "usable catalogue". M3 = S05-S06 "maintainable". M4 = S07 usability study, release.

## 7. Deferred
REQ-14 accounts, community, uploads, auto-submit, probability scores, mobile app, worldwide coverage. No plans produced.

## 8. Blocking decisions
Before S01: confirm D-02 (stack). Before S06: maintainer authentication method. Before S07: final destination list and opportunity list.
