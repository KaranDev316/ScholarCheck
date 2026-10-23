# CONTEXT.md — Autonomous Scholarship Platform

> Direction updated **23 Oct 2026** (D-09 and D-10). Publication can be
> source-backed without routine human approval. The first release is a public
> four-scholarship website; one-record monitoring follows; discovery follows
> proven monitoring. `PUBLICATION-POLICY.md` defines the publication gate.

## 1. Project
- **Name:** NOT DECIDED (working title: "ScholarCheck")
- **Purpose:** Continuously discover, validate and maintain scholarship opportunities from official sources, then help students judge them with evidence they can check. [D-09]
- **Target user:** International applicants seeking funded **bachelor's, master's or doctoral (PhD)** degrees. First test profile: Malawian national, resident in India, three-year BCA. [ASSUMED D-08; the source audit covered research master's only]
- **Problem:** Aggregator listings blur funding (tuition exemption shown as "fully funded"), flatten multi-stage deadlines into one date, bury blocking eligibility conditions, and label article links "Apply Now". [SOURCE]
- **Status:** S01 scaffold, four unverified seed fixtures, PostgreSQL loader and a development-only read endpoint exist; public publication and monitoring are not implemented.
- **Nature:** Portfolio project built and maintained by one person, designed so it could become a real product. [ASSUMED D-01]

## 2. MVP boundary
First publish the four existing scholarships through source-backed validation
and launch a public, no-account site for browsing, search, country/level/funding
filters, eligibility, deadlines, evidence, official application links and
sharing. Then monitor one published scholarship until it can safely update or
hold a meaningful change unattended. Expand monitoring to the other three
before adding automatic discovery. Profiles, personal assessments and saving
are later features. Detail lives in `PRP.md` and `ROADMAP.md`. [D-10]

## 3. Confirmed / assumed stack
| Layer | Choice | Why | Status |
|---|---|---|---|
| Frontend | React + TypeScript (Vite SPA) | Typed UI, simple static hosting | [ASSUMED D-02, from audit proposal] |
| Backend | FastAPI (Python) | Typed request/response models, fast to build | [ASSUMED D-02] |
| Data | PostgreSQL | Relational model (opportunity / round / programme / rule / evidence) | [ASSUMED D-02] |
| Auth | Optional maintainer access and applicant accounts undecided | Routine publication runs without human login; account sync is deferred (D-05) | [ASSUMED] |
| Extraction | Deterministic parsers first; model-assisted extraction may propose candidates | Independent validation gates decide publication, never model confidence alone | [D-09] |
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
- Optional human review may resolve exceptions but is not a routine gate.

## 5. Domain rules (must hold across all slices) [SOURCE]
1. Four eligibility outcomes only: *Meets checked requirements*, *Potential fit: confirmation needed*, *Does not meet a stated requirement*, *Insufficient information*. Each shows its reason. **No match percentage or win probability.**
2. Eligibility, funding suitability, application availability and competitiveness are separate assessments.
3. Funding is shown per component (tuition, living, accommodation, insurance, travel, upfront costs, renewal, funding relationship). A tuition exemption is never called a stipend. Components are never summed into a single "you receive" total.
4. Deadlines belong to a route and intake and have a stage (EOI, admission, scholarship, nomination, university). Exact time/zone only when published. States: not announced, rolling, closed, needs rechecking. Closing one round never closes another.
5. Every decision-critical claim has traceable official-source evidence.
   `retrieved_at`, automated `source_checked_at` and human `verified_at` are
   different events. Automatic work never sets `verified_at` or `verified_by`.
6. Grades keep their original scale; no universal conversion. Unresolved degree recognition stays **unknown**. "International students accepted" does not imply a three-year degree is accepted.
7. "Submitted" and decision states are user-reported only.
8. An unavailable source keeps previous data with a visible recheck warning.
9. Publishing requires every deterministic gate in
   `PUBLICATION-POLICY.md`. Insufficient evidence holds a new candidate or
   preserves the last-known-good published revision.

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
| D-09 | Automatic source-backed publication; human review optional | Routine operation cannot require the owner to approve every update. Failed gates hold or reject; fetch failures retain last-known-good. Human verification fields remain human-only. | Owner direction, 23 Oct 2026 |
| D-10 | Public four-scholarship MVP first, then reliable one-record monitoring, then discovery | Get a useful site running; prove a meaningful change can update or hold safely without intervention before expanding coverage | Owner direction, 23 Oct 2026 |

## 10. Current status / next action
S01 scaffold, fixtures, PostgreSQL storage and development read endpoint exist.
The fixture review found material route, wording and deadline issues; none is
yet eligible for publication. Next: resolve fixture issues, build source-backed
publication and public catalogue/detail journeys, then monitor one record.

## 11. Open (nonblocking) questions
Hosting and snapshot storage provider; source access policy; monitoring
cadence; UI library; whether accounts ever ship.
