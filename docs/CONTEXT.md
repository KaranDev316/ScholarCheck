# CONTEXT.md — Scholarship Decision Tool

> Status: **PROPOSED**. Items marked **[ASSUMED]** were chosen to unblock planning and are not yet approved. Items marked **[SOURCE]** come from the market audit dated 23 Oct 2026. Overturn any assumption by editing the decision log (section 9); downstream documents trace back to its IDs.

## 1. Project
- **Name:** NOT DECIDED (working title: "ScholarCheck")
- **Purpose:** Help students judge which funded scholarships are worth pursuing, with evidence they can check. [SOURCE]
- **Target user:** International applicants seeking funded **research master's** degrees. First test profile: Malawian national, resident in India, three-year BCA. [SOURCE]
- **Problem:** Aggregator listings blur funding (tuition exemption shown as "fully funded"), flatten multi-stage deadlines into one date, bury blocking eligibility conditions, and label article links "Apply Now". [SOURCE]
- **Status:** Concept + audit. No repository exists. Greenfield. [ASSUMED]
- **Nature:** Portfolio project built and maintained by one person, designed so it could become a real product. [ASSUMED D-01]

## 2. MVP boundary
20-30 carefully checked research-master's funding opportunities across **Canada, Australia, Germany** [ASSUMED D-03], with structured listings, official evidence, filters, requirement-by-requirement assessment, funding breakdown, intake-aware deadlines, comparison of up to three, a personal checklist/next action, and internal review tools. Detail lives in `PRP.md`.

## 3. Confirmed / assumed stack
| Layer | Choice | Why | Status |
|---|---|---|---|
| Frontend | React + TypeScript (Vite SPA) | Typed UI, simple static hosting | [ASSUMED D-02, from audit proposal] |
| Backend | FastAPI (Python) | Typed request/response models, fast to build | [ASSUMED D-02] |
| Data | PostgreSQL | Relational model (opportunity / round / programme / rule / evidence) | [ASSUMED D-02] |
| Auth | NOT DECIDED for S01-S06; optional accounts deferred (D-05) | Browse and save without registration | [ASSUMED] |
| AI | **NOT APPLICABLE in MVP** | A human approves every eligibility, funding and deadline claim | [ASSUMED D-06; SOURCE supports human approval] |
| UI library | NOT DECIDED | | |
| Hosting | NOT DECIDED; low-cost, single deployable | | |
| Background worker | NOT APPLICABLE until recurring recheck slice (S06) | | [SOURCE] |

## 4. Architecture and data boundaries
- Single application first; no microservices. [SOURCE]
- **Domain entities:** Opportunity (stable scheme), Round (intake/year/route), Programme (funded degree), EligibilityRule, FundingComponent, Deadline, Evidence, ChangeRecord. Saved-application state belongs to the user. [SOURCE]
- Opportunity, Round and Programme must stay separate. [SOURCE]
- **User state (profile, shortlist, checklist) is stored client-side in the MVP** [ASSUMED D-04]; the server evaluates a submitted profile statelessly and stores no personal data. Accounts for cross-device sync are a later `Should`.
- Catalogue content is seeded from reviewed files in the repository and loaded into PostgreSQL; edits go through review. [ASSUMED D-07]

## 5. Domain rules (must hold across all slices) [SOURCE]
1. Four eligibility outcomes only: *Meets checked requirements*, *Potential fit: confirmation needed*, *Does not meet a stated requirement*, *Insufficient information*. Each shows its reason. **No match percentage or win probability.**
2. Eligibility, funding suitability, application availability and competitiveness are separate assessments.
3. Funding is shown per component (tuition, living, accommodation, insurance, travel, upfront costs, renewal, funding relationship). A tuition exemption is never called a stipend. Components are never summed into a single "you receive" total.
4. Deadlines belong to a route and intake and have a stage (EOI, admission, scholarship, nomination, university). Exact time/zone only when published. States: not announced, rolling, closed, needs rechecking. Closing one round never closes another.
5. Every decision-critical claim has evidence (source URL, supporting passage, retrieved-at, verified-at, verified-by). Retrieved-at and verified-at are separate; an automatic refresh never sets verified-at.
6. Grades keep their original scale; no universal conversion. Unresolved degree recognition stays **unknown**. "International students accepted" does not imply a three-year degree is accepted.
7. "Submitted" and decision states are user-reported only.
8. An unavailable source keeps previous data with a visible recheck warning.

## 6. Coding standards [ASSUMED unless noted]
- TypeScript `strict`; Python 3.12 with type hints; no `any` without a comment.
- Pydantic models for every API boundary; validate all input server-side.
- Errors: structured JSON `{code, message, details?}`; never expose stack traces; UI shows plain-language messages.
- Names: `snake_case` Python, `camelCase` TS variables, `PascalCase` components/types; REQ/AC/T IDs referenced in test names.
- Tests: pytest (backend), Vitest + Testing Library (frontend), one end-to-end smoke test per slice (tooling NOT DECIDED).
- Accessibility: keyboard operable, labelled inputs, outcome conveyed by text not colour alone.
- Secrets only via environment variables; never committed. Env var names (proposed): `DATABASE_URL`, `APP_ENV`, `CORS_ALLOWED_ORIGINS`.
- No new packages, framework upgrades or unrelated refactors inside a slice.

## 7. Repository layout [ASSUMED]
```
/docs            CONTEXT.md PRP.md ROADMAP.md slices/S##/{VERIFICATION,PLAN,EVIDENCE}.md
/backend         app/ (api, domain, models) tests/
/frontend        src/ (pages, components, api, state) tests/
/content         opportunities/*.yaml  (reviewed seed data)
```

## 8. Constraints and non-goals
Out: open community, document uploads, automatic submission, probability scores, native mobile app, worldwide coverage, copying competitors' code or text, scraping private sources, AI-approved eligibility.
Constraint: link to official sources; write own summaries.

## 9. Decision log
| ID | Decision | Rationale | Source / approval |
|---|---|---|---|
| D-01 | Portfolio-first, product-capable | Matches audit's framing and one-person capacity | Assumed |
| D-02 | React+TS / FastAPI / PostgreSQL | Audit recommendation | Assumed |
| D-03 | Canada, Australia, Germany | Audit examples (CA, AU) + DAAD benchmark | Assumed |
| D-04 | Client-side user state, no accounts in MVP core | Audit: browse without registration; avoids storing PII | Assumed |
| D-05 | Accounts deferred (Should) | Not needed to prove core advantage | Assumed |
| D-06 | No AI in MVP | Audit: human approves claims first | Assumed |
| D-07 | Content seeded via reviewed files, internal review tool in S06 | Maintainable alone | Assumed |

## 10. Current status / next action
Planning set drafted: PRP → ROADMAP → S01 VERIFICATION → S01 PLAN. Next action: approve or amend D-01..D-07, then begin S01.

## 11. Open (nonblocking) questions
Product name; hosting provider and budget; UI library; test tooling for E2E; which 20-30 opportunities; whether accounts ever ship.
