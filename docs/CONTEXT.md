# CONTEXT.md — Autonomous Scholarship Platform

> Direction updated **24 Oct 2026** (D-11). Publication is fully automated,
> with no human-verification workflow. The first release is a public website
> with a small set of best-evidenced scholarships; one-record monitoring follows,
> then discovery. `PUBLICATION-POLICY.md` defines the publication gate.

## 1. Project
- **Name:** NOT DECIDED (working title: "ScholarCheck")
- **Purpose:** Help students find funding and check exact official-source evidence. Automated monitoring and discovery grow the catalogue after the public MVP. [D-10, D-11]
- **Target user:** International applicants seeking funded **bachelor's, master's or doctoral (PhD)** degrees. First test profile: Malawian national, resident in India, three-year BCA. [ASSUMED D-08; the source audit covered research master's only]
- **Problem:** Aggregator listings blur funding (tuition exemption shown as "fully funded"), flatten multi-stage deadlines into one date, bury blocking eligibility conditions, and label article links "Apply Now". [SOURCE]
- **Status:** S01 scaffold, four unverified seed fixtures, PostgreSQL loader and a development-only read endpoint exist; public publication and monitoring are not implemented.
- **Nature:** Portfolio project built and maintained by one person, designed so it could become a real product. [ASSUMED D-01]

## 2. MVP boundary
Publish a small set of the best-evidenced scholarships through source-backed
validation and launch a public, no-account site for browsing, search,
country/level/funding-type filters, stated eligibility, deadlines, exact
evidence, official application links and sharing. Keep the four existing
fixtures for regression, replacing weak launch candidates as needed. Then
monitor one published scholarship until it can update or hold a meaningful
change unattended. Expand monitoring before automatic discovery. Profiles,
personal assessments and saving are later features. [D-10, D-11]

## 3. Confirmed / assumed stack
| Layer | Choice | Why | Status |
|---|---|---|---|
| Frontend | React + TypeScript (Vite SPA) | Typed UI, simple static hosting | [ASSUMED D-02, from audit proposal] |
| Backend | FastAPI (Python) | Typed request/response models, fast to build | [ASSUMED D-02] |
| Data | PostgreSQL | Relational model (opportunity / round / programme / rule / evidence) | [ASSUMED D-02] |
| Auth | No accounts in first release | Automated publication has no reviewer login; later applicant account sync is deferred | [D-11] |
| Extraction and checking | Parsers plus AI candidate extraction and a separate AI evidence-check pass | Code checks retained excerpts, values, context and policy gates before publication; model confidence alone never decides | [D-11, clarified 24 Oct 2026] |
| UI library | NOT DECIDED | | |
| Hosting | NOT DECIDED; low-cost, single deployable | | |
| Workers | Python scheduled jobs, initially simple | Fetch, extract, validate and retry independently of user requests | [D-09; implementation pending] |
| Snapshots | Object storage or an equivalent immutable store | Retain source content used for each publication decision | [D-09; provider undecided] |

## 4. Architecture and data boundaries
- Single application first; no microservices. [SOURCE]
- **Domain entities:** Opportunity (stable scheme), Round (intake/year/route), Programme (funded degree), EligibilityRule, FundingComponent, Deadline, Evidence, ChangeRecord. Saved-application state belongs to the user. [SOURCE]
- Opportunity, Round and Programme must stay separate. [SOURCE]
- The first release has no applicant account or profile. Any later profile,
  shortlist or checklist state may be stored client-side; cross-device sync
  remains deferred. [D-10; prior D-04 assumption narrowed]
- The four YAML fixtures are regression benchmarks. Production candidates come
  from registered official sources and pass `PUBLICATION-POLICY.md` before
  publication. PostgreSQL stores current records and revision metadata;
  immutable snapshots preserve the evidence. [D-09]
- The owner architecture is official government, university and approved
  scholarship NGO sources → collector → retained snapshots → AI extraction and
  evidence checking → deterministic publication gates → PostgreSQL →
  published-only API → website. See `ARCHITECTURE.md`. [D-12]
- There is no human-verification workflow or UI. Missing or conflicting
  material evidence holds publication automatically. [D-11]

## 5. Domain rules (must hold across all slices) [SOURCE]
1. Four eligibility outcomes only: *Meets checked requirements*, *Potential fit: confirmation needed*, *Does not meet a stated requirement*, *Insufficient information*. Each shows its reason. **No match percentage or win probability.**
2. Eligibility, funding suitability, application availability and competitiveness are separate assessments.
3. Funding is shown per component (tuition, living, accommodation, insurance, travel, upfront costs, renewal, funding relationship). A tuition exemption is never called a stipend. Components are never summed into a single "you receive" total.
4. Deadlines belong to a route and intake and have a stage (EOI, admission, scholarship, nomination, university). Exact time/zone only when published. A date without a year is never treated as open; a past date reads “Date passed” for that round only. Other rounds remain independent.
5. Every decision-critical claim has exact retained official-source evidence.
   `retrieved_at` and automated `source_checked_at` are different events.
   Legacy human-verification fields are scheduled for removal. Each material
   fact has `stated`, `unspecified` or `conflicting` state rather than a bare
   null in the publication contract.
6. Grades keep their original scale; no universal conversion. Unresolved degree recognition stays **unknown**. "International students accepted" does not imply a three-year degree is accepted.
7. "Submitted" and decision states are user-reported only.
8. An unavailable source keeps previously supported public data and its real
   checked date; the pipeline records a recheck warning internally.
9. Publishing requires every deterministic gate in
   `PUBLICATION-POLICY.md`. Insufficient evidence holds a new candidate or
   preserves the last supported published revision.
10. “Fully funded” requires explicit official evidence for tuition, living
    costs and flights. Funding types are Fully funded, Tuition + stipend and
    Tuition; an unsupported category remains unassigned.

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
/content         opportunities/*.yaml  (unverified regression fixtures)
```

## 8. Constraints and non-goals
Out: open community, document uploads, automatic application submission,
probability scores, native mobile app, worldwide coverage, copying competitors'
code or text, scraping private sources, or publishing on AI confidence alone.
Constraint: link to official sources; write own summaries.

## 9. Decision log
| ID | Decision | Rationale | Source / approval |
|---|---|---|---|
| D-01 | Portfolio-first, product-capable | Matches audit's framing and one-person capacity | Assumed |
| D-02 | React+TS / FastAPI / PostgreSQL | Audit recommendation | Assumed |
| D-03 | Canada, Australia, Germany | Audit examples (CA, AU) + DAAD benchmark | Assumed |
| D-04 | Client-side user state, no accounts in MVP core | Audit: browse without registration; avoids storing PII | Assumed |
| D-05 | Accounts deferred (Should) | Not needed to prove core advantage | Assumed |
| D-06 | Superseded by D-09: no AI in MVP | Human-only review cannot support unattended operation | Superseded 23 Oct 2026 |
| D-07 | Superseded by D-09: reviewed files as production source | Keep YAML as regression fixtures; production uses source snapshots and policy gates | Superseded 23 Oct 2026 |
| D-08 | Degree levels: bachelor's, master's (taught or research) and doctoral (PhD) | Every level the product should serve is in scope; levels stay distinct, so a programme is never matched across levels and a rule that names a level is evaluated only against that level | Owner request, 23 Oct 2026 |
| D-09 | Automatic source-backed publication; human review initially optional | Routine operation cannot require owner approval. Superseded in part by D-11, which removes human verification entirely. | Owner direction, 23 Oct 2026 |
| D-10 | Public MVP first, then reliable one-record monitoring, then discovery | Get a useful site running; prove a meaningful change can update or hold safely before expanding coverage | Owner direction, 23 Oct 2026 |
| D-11 | Fully automated, evidence-first public product with strict coverage labels | No human-verification workflow; launch the best-evidenced records; enforce exact excerpts, fact states, computed funding types and a three-part “Fully funded” gate | Owner wireframe decisions and launch-set choice, 24 Oct 2026 |
| D-12 | Source-to-website architecture with collector and AI validation | Accept government, university and approved scholarship NGO sources; retain snapshots; code gates publication between AI proposals and published revisions/API | Owner architecture diagram, 24 Oct 2026 |

## 10. Current status / next action
S01 scaffold, fixtures, PostgreSQL storage and development read endpoint exist.
The fixture review found material route, wording and deadline issues; none is
yet eligible for publication. Next: migrate legacy human-verification fields,
implement strict evidence and coverage gates, select best-evidenced launch
records, and build the public catalogue/detail journeys. Then monitor one.

## 11. Open (nonblocking) questions
Hosting and snapshot storage provider; provider allowlist/access policy;
monitoring cadence; real domain and contact details; whether no paid listings
is a true business commitment; whether accounts ever ship.
