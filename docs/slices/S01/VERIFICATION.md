# S01 VERIFICATION — One Complete Decision

## 1. Scope and traceability
- **Slice:** S01. **REQ:** 01, 02, 03, 04, 06, 08.
- **In scope:** enter profile; open a fixture opportunity; see assessment, funding breakdown, official links, evidence; save with a next action and note.
- **Excluded:** filters, comparison, tracker/checklist, round-level deadline logic and freshness warnings (S02), admin, accounts.
- **Assumptions:** A1 profile and saved items live in browser storage (D-04). A2 3-4 fixture records are human-verified against official sources before demo; fixtures cover: an enrolment-only doctoral award, a tuition-exemption scheme, a multi-stage EOI scheme, a stipend-plus-fee scheme. A3 listings show date information as-published but no deadline *status logic* until S02.
- **Dependencies:** D-02 confirmed; fixtures researched.

## 2. Acceptance scenarios
**AC-01 Valid profile saved.** Actor: student. Pre: none. Action: submit nationality, residence, degree type, duration, status, intended level. Success: profile confirmed on screen and survives reload. Side effects: profile in browser only; no server record. Evidence: UI screenshot, storage inspection.

**AC-02 Profile validation.** Action: submit with a required field empty or an unrecognised country. Result: field-level message; profile not saved; no assessment run. Evidence: UI test, screenshot.

**AC-03 Grade keeps original scale.** Action: enter "8" with scale "10-point CGPA". Result: shown exactly as entered; no converted value anywhere. Evidence: UI test, API response inspection.

**AC-04 Open listing.** Pre: fixture exists. Action: open it. Result: scheme, programme, round and funder shown; decision information (requirements blockers, funding) appears before descriptive text; "Read summary", "Official requirements", "Application portal" are distinct actions pointing to official URLs. Evidence: screenshot, link check.

**AC-05 Unknown opportunity.** Action: open a non-existent id. Result: not-found message with route back; no crash. Evidence: UI + API example (error code agreed; see §5).

**AC-06 Enrolment-only blocker visible first.** Pre: profile with no Canadian doctoral enrolment; open the enrolled-applicants-only fixture. Result: blocking condition displayed at the top; outcome is *Does not meet a stated requirement* with that rule named. Evidence: screenshot, automated test.

**AC-07 Unresolved degree recognition stays unknown.** Pre: profile with three-year BCA; fixture whose published requirements do not state whether it qualifies. Result: outcome *Potential fit: confirmation needed*, reason names the degree-recognition rule; never *Meets*. Evidence: automated test, screenshot.

**AC-08 Outcome vocabulary.** For all fixtures and varied profiles, overall outcome is exactly one of the four defined values; no percentage or probability appears. Evidence: automated test over matrix of profiles, UI scan.

**AC-09 No profile.** Action: open listing without a profile. Result: rules listed with "Insufficient information" and a prompt to enter a profile. Evidence: screenshot, test.

**AC-10 Funding by component.** Pre: tuition-exemption fixture. Result: exemption shown under Tuition with amount/currency/period, labelled as a reduction of tuition; Living support shows "Unspecified"; no total, no word "stipend" attached to it. For the stipend fixture: stipend, tuition support and other items appear separately; accommodation not shown as free unless the source says so. Evidence: screenshot, automated data-to-UI test.

**AC-11 Evidence per claim.** Action: open evidence for a funding component, an eligibility rule and a date. Result: source link, supporting passage, retrieved-at and verified-at (labelled separately). A claim without evidence shows "Unverified" and cannot contribute to a "confirmed" label. Evidence: screenshot, test with an evidence-less rule.

**AC-12 Save with next action.** Action: save an opportunity with a next action and note. Result: appears in saved list; persists after reload; saved record stores the opportunity id and round. Evidence: UI test, storage inspection.

**AC-13 Storage unavailable.** Pre: storage blocked. Action: save. Result: clear message that saving is unavailable; profile entry and assessment still usable in-session; no silent loss. Evidence: automated test with storage disabled.

**AC-14 Assessment service failure.** Pre: assessment call fails. Result: listing still renders with static facts; assessment area shows a retryable error; no fabricated outcome. Evidence: test with forced failure, screenshot.

## 3. Business invariants
1. Unresolved rules never become satisfied. 2. Missing data is shown as unknown/unspecified, never zero or full. 3. No score, percentage or probability. 4. Eligibility, funding and (later) availability are shown separately. 5. Evidence timestamps retrieved vs verified are never merged. 6. No grade conversion. 7. Assessment is a pure function of (profile, opportunity): same inputs, same outputs (idempotent, no server state). 8. No personal profile data persisted server-side.

## 4. Failure and recovery
Assessment failure → listing remains, assessment retryable, no partial outcome shown. Storage failure → in-session use, visible notice. Content load failure → not-found/error state. Rollback/compensation: **NOT APPLICABLE** (no multi-step write transactions; fixture loading is a build step).

## 5. Interfaces and compatibility
No external API contracts are approved yet. **Open (not invented):** the exact error status/body for not-found and validation, and the response shape for assessment, must be agreed in T02/T07 and recorded here as an amendment before implementation of T07. Externally visible behavior is as stated in the ACs.

## 6. Nonfunctional acceptance
- **Privacy:** profile not sent for storage; assessment request not logged with profile contents (verify in logs).
- **Accessibility:** form operable by keyboard, labelled fields, errors announced, outcomes readable without colour. WCAG target TBD.
- **Reliability/performance:** TBD, no thresholds set.
- **Observability:** server logs request id, route, status; no profile data.
- **Auth:** none in S01 (public read).

## 7. Manual review checklist
1. Open home; no profile → listing shows prompt (AC-09). 2. Submit empty profile (AC-02). 3. Enter P1: Malawi / India / BCA / 3 years / ongoing / research master's (AC-01, 03). 4. Open each fixture and read top-of-page content (AC-04, 06, 07, 10). 5. Click each evidence control (AC-11). 6. Click all three link types. 7. Save, reload, confirm (AC-12). 8. Block storage and retry (AC-13). 9. Stop the backend and reopen a listing (AC-14). 10. Open bad id (AC-05).

## 8. Proof checklist
| AC | Automated type | Manual / artifact |
|---|---|---|
| 01,02,03 | component + API validation tests | screenshots |
| 04 | component test, link check | screenshot |
| 05 | API + UI test | screenshot |
| 06,07,08,09 | unit tests on evaluator matrix; component tests | screenshots |
| 10 | data-to-UI test | screenshots |
| 11 | component test | screenshots |
| 12,13 | UI tests with storage fixtures | storage inspection |
| 14 | UI test with mocked failure | screenshot |
Evidence will be recorded in `EVIDENCE.md`; none exists yet.

## 9. Definition of Done
All AC pass; automated checks green; no domain-rule regression; failures handled; changes within S01 scope; fixtures verified against official sources; evidence recorded; independent audit complete.
