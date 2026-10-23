# S01 PLAN — Atomic Prompt Chain

Inputs: `CONTEXT.md`, `ROADMAP.md` (S01), `slices/S01/VERIFICATION.md`. Greenfield repository.

**Common preamble (prepend to every step's prompt):**
> Read `docs/CONTEXT.md`, `docs/slices/S01/VERIFICATION.md` and the relevant ROADMAP section. Inspect the existing repo first. Make only this step's change, follow the stated conventions, add no new packages beyond those listed, do no unrelated refactors or formatting. Write or update tests for the behaviour. Run the stated checks. Return: diff summary, exact commands and their real output, remaining risks. Do not commit. Do not say a check passed unless you ran it. If the step's pause condition applies, stop and ask.

---
## Step 1 — Scaffold and domain types
- **Purpose:** Working skeleton and the shared contract everything else uses.
- **IDs:** T01, T02. Enables all AC.
- **Prompt:** Create `/backend` (FastAPI, pytest), `/frontend` (React+TS strict, Vite, Vitest + Testing Library), `/content`, and `/docs` placeholders per CONTEXT section 7. Define domain types: Opportunity, Programme, Round (identity only), EligibilityRule (requirement text, kind, blocking flag, evidence refs), FundingComponent (component, status: specified/partial/unspecified, amount/currency/period, conditions, evidence refs), Evidence (url, passage, retrieved_at, verified_at, verified_by nullable), Profile, AssessmentResult with the four outcome values and per-rule result+reason. Backend health route and a frontend page that renders. Propose, but do not finalise, the assessment response shape and error body; list them in your report.
- **Expected outcome:** both apps start; type checks and empty test suites run.
- **Verify:** `pytest`, `npm run test`, `npm run build`, `npx tsc --noEmit`; both dev servers start.
- **Pause if:** the stack differs from D-02, or the response shape is ambiguous. **Gate:** the proposed assessment and error shapes are approved and appended to VERIFICATION §5.

## Step 2 — Fixture content and read path
- **Purpose:** Real data flowing from file to API.
- **IDs:** T03, T04, T05; AC-04, AC-05, AC-10, AC-11 (data side).
- **Prompt:** Define the YAML seed format in `/content/opportunities`. Create the 3-4 fixture records listed in VERIFICATION A2 using values from `docs/` audit notes marked "unverified until a human checks the official source", including evidence fields with null `verified_at`. Add a PostgreSQL schema and a loader. Add `GET` read for one opportunity and a not-found response in the approved error shape.
- **Outcome:** each fixture retrievable; unknown id returns the agreed not-found response.
- **Verify:** loader test, API tests for found/not found, evidence timestamps stay separate.
- **Pause if:** a source fact is not in the repository docs. Do not invent values: leave `unspecified`.

## Step 3 — Assessment evaluator (core logic)
- **Purpose:** The product's central, riskiest behaviour as a pure function.
- **IDs:** T06; AC-06, AC-07, AC-08, AC-09; invariants 1, 2, 3, 6, 7.
- **Prompt:** Implement `evaluate(profile, opportunity) -> AssessmentResult` with no I/O. Rules: unresolved rule can never be satisfied; any unmet blocking rule yields *Does not meet a stated requirement*; otherwise any unresolved rule yields *Potential fit: confirmation needed*; no profile yields *Insufficient information*; all checked rules satisfied yields *Meets checked requirements*. Rules lacking evidence cannot produce "meets". Never convert grades. Unit-test a matrix of profiles × fixtures, including P1 against each fixture.
- **Outcome:** deterministic results with reasons.
- **Verify:** `pytest -k evaluator`; property check that outcome is always one of four values and repeated calls are identical.
- **Pause if:** a rule kind cannot be evaluated from stated data (ask whether it should be unresolved).

## Step 4 — Assessment endpoint with validation and failure handling
- **Purpose:** Expose the evaluator safely.
- **IDs:** T07; AC-02 (server side), AC-14; privacy NFR.
- **Prompt:** Add the assessment endpoint using the approved shape. Validate profile server-side (required fields, known country, degree status values, optional grade with scale). Return structured errors. Ensure logs contain request id, route, status only. Test valid, invalid, unknown opportunity, and forced evaluator error.
- **Outcome:** consistent success and error responses; no profile data in logs.
- **Verify:** API tests; manually inspect captured logs from a test run.
- **Pause if:** validation rules for "degree type" or "country list" are not defined (ask for the enumerations).

## Step 5 — Frontend: profile, listing, evidence, save
- **Purpose:** The visible decision path.
- **IDs:** T08, T09, T10; AC-01, 02, 03, 04, 05, 06, 07, 09, 10, 11, 12, 13, 14.
- **Prompt:** Build in order: profile form with local persistence; listing page showing blockers and outcome first, then funding components, then deadlines as published, then official-link actions (summary, requirements, portal as distinct); evidence panel showing retrieved vs verified separately and "Unverified" when absent; save with next action and note to browser storage with storage-unavailable handling; assessment-failure state keeping static facts. Outcomes use text, not colour alone; keyboard operable. Component tests for each state.
- **Outcome:** full demo path works for persona P1 against the fixtures.
- **Verify:** `npm run test`, `npx tsc --noEmit`, manual checklist VERIFICATION §7 items 1-10.
- **Pause if:** copy for outcomes or funding labels is ambiguous (do not rename the four outcomes).

## Step 6 — Full acceptance, regression and handoff
- **Purpose:** Prove every AC and prepare for independent audit.
- **IDs:** T11; AC-01..AC-14.
- **Prompt:** Add one E2E smoke test along the demo path. Run all automated suites. Walk the manual checklist, capturing screenshots and API examples into `docs/slices/S01/EVIDENCE.md` mapped to each AC; mark any AC unproven honestly. Confirm no out-of-scope files or packages were added. Summarise risks.
- **Outcome:** `EVIDENCE.md` with AC → evidence mapping.
- **Verify:** `pytest`, `npm run test`, E2E command, `git status` shows only S01 areas.
- **Pause if:** any AC fails, or fixture data is not yet human-verified (record as release blocker, not a pass).

---
## Coverage matrix
| AC | Steps |
|---|---|
| 01, 03 | 5, 6 |
| 02 | 4, 5, 6 |
| 04, 05 | 2, 5, 6 |
| 06, 07, 08, 09 | 3, 5, 6 |
| 10, 11 | 2, 5, 6 |
| 12, 13 | 5, 6 |
| 14 | 4, 5, 6 |

## End-of-slice regression
Re-run all unit/API/component tests; E2E smoke; confirm invariants 1-8 with the evaluator matrix; spot-check P1 on all fixtures; confirm no profile data in server logs.

## Expected `EVIDENCE.md`
Per AC: test names and output, screenshots, API samples, log excerpt, storage inspection, link check results, fixture-verification notes.

## Risks / likely files
Evaluator logic and seed data accuracy are the main risks. Files: `backend/app/{domain,api,models}`, `backend/tests`, `frontend/src/{pages,components,api,state}`, `frontend/tests`, `content/opportunities/*.yaml`, `docs/slices/S01/*`.

## Ready for implementation?
**BLOCKED (soft):** start Step 1 now; before Step 2 finalise the response/error shapes (Step 1 gate), and before release a human must verify the fixtures against official pages. Stack decision D-02 is assumed, not approved.
