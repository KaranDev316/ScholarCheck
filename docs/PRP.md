# PRP.md — Product requirements

Depends on `CONTEXT.md` decisions D-09..D-11 and
`PUBLICATION-POLICY.md`. `ROADMAP.md` defines delivery order. The product
wireframe decisions supplied on 24 October 2026 govern the first-release UI.
The [local wireframe export](design/scholarcheck-product-wireframe.html) is a
visual reference with sample content. The supplied decisions are the source of
truth for implementation.

## Product and audience

**Find funding. Check the evidence. Decide for yourself.** ScholarCheck is a
public, no-account website for applicants seeking a degree after grade 12:
Bachelor's, Master's or PhD. It shows a small number of useful facts per
scholarship, alongside exact official wording and visible unknowns. It does
not decide whether a particular visitor qualifies.

## First-release requirements (Stage 1)

| ID | Requirement | Acceptance |
|---|---|---|
| MVP-01 | Public catalogue | Visitors browse published scholarships without signing in; held fixtures never appear |
| MVP-02 | Search and filters | Search title/provider and doctoral synonyms; filter by destination country, study level and funding type; removable active filters and clear-filters empty state work |
| MVP-03 | Scholarship detail | Stable direct URL shows scheme, provider, applicable level, round, headline funding component and amount, stated eligibility, separate funding components, deadlines, exact evidence and the latest source-check date |
| MVP-04 | Official actions | “Read the requirements” and “Apply on the provider's site” are distinct only when they lead to distinct confirmed destinations; passed dates or an unavailable route show a plain explanation, never a misleading disabled application button |
| MVP-05 | Sharing | Text-labelled Copy link and Share controls use the real canonical scholarship URL and open the same public detail page |
| MVP-06 | Evidence-backed publication | AI extracts candidate facts and a separate AI pass checks whether retained official wording supports each claim; deterministic gates in `PUBLICATION-POLICY.md` make the final publish/hold decision; missing or conflicting evidence holds automatically |
| MVP-07 | Honest unknowns and dates | Facts distinguish stated, unspecified and conflicting; a date without a year never implies an open round; a passed date affects only its own round and is labelled “Date passed” |
| MVP-08 | Funding classification | Components stay separate in provider currency; the coverage checklist shows Tuition, Living costs and Flights as Covered or Not stated only when evidence supports each; the computed “Fully funded” chip requires all three |
| MVP-09 | Public quality | Keyboard access, mobile layout, system light/dark theme, clear loading/error states, source-check wording rather than internal pipeline details, and no claims beyond the stored decision |
| MVP-10 | Problem reports | “See something wrong?” accepts a report through a working feedback endpoint, with a clear success/error result and abuse controls |

### Funding type and amount rules

The filters and tags are **Fully funded**, **Tuition + stipend**, and
**Tuition**, in that order. “Grant,” “Stipend” alone and “Tuition reduction”
are not filter categories. An opportunity can remain published without one of
these three tags when the source does not establish a category; do not infer
tuition coverage merely to fill a filter. The “Fully funded” chip is computed
only when official evidence explicitly establishes tuition, living costs and
flights coverage. The badge disappears if a later supported revision removes
any one of those claims. No amounts are summed, converted or ranked across
currencies. A headline amount always names its component and basis, such as
“Annual stipend.” A tuition exemption must state which charges it covers.

### Study levels

Filter options are Bachelor's, Master's and PhD. “Research degree” is a
temporary fallback only where the official source does not distinguish
Master's from PhD. A record may have several evidenced levels and appears
under each. “Doctoral” and “doctorate” searches find PhD records. Diplomas
and postdoctoral fellowships are outside the first release.

### Public screens

- **Home:** navy hero, the product promise, one sentence about official
  wording, search, no-account note, a real evidence-backed example card, quick
  filters and published scholarships. No pipeline explainer or stats row.
- **Find scholarships:** search; country, level and funding-type filters;
  removable active chips; cards with provider/country, title, tags, component
  amount and basis, actual checked date, and a detail link. Loading, error and
  empty states use real API state.
- **Scholarship page:** breadcrumb; title and text-labelled share controls; summary strip;
  distinct official actions; funding coverage checklist and components;
  stated eligibility disclaimer; round/date/status table; exact retained
  evidence; source-check panel; at-a-glance facts; and a working problem-report
  dialog. A phone layout keeps the primary official action reachable.
- **Navigation:** Home and Find scholarships. No account, “How we check” page,
  theme switch, preview banner, or saved-item controls in this release.

Student-facing copy shows the source, exact passage, saved/check date and a
plain result such as “Matches the official page.” Claim counts, policy version,
revision number and gate explanations stay in the internal decision trail.
Do not show a human-verification label or panel.

### Visual direction

Navy `#0D173B`, off-white `#F8F9FA`, gold `#D4AF37`; navy dominates the
header, hero, footer and source-check panel. White cards sit on off-white.
Gold is reserved for primary actions, thin rules and the
“Fully funded” chip, never body text on off-white. Focus outlines are navy.
Headings use Iowan Old Style/Charter/Georgia fallback; body uses system sans.
Follow the visitor's system light/dark setting, with no theme switch. An
amber hatched “Not specified” treatment makes unknowns visibly distinct from
positive facts. Check contrast and keyboard focus in both themes.

## Reliable update requirements (Stage 2)

| ID | Requirement | Acceptance |
|---|---|---|
| MON-01 | Register one official source | Identity, access permission, URL and schedule are recorded |
| MON-02 | Fetch and compare | Immutable snapshots and hashes distinguish unchanged, changed and failed fetches; unchanged content makes no new revision |
| MON-03 | Validate meaningful changes | Changed material claims link to exact new excerpts and pass the same gates as initial publication |
| MON-04 | Safe decision | Supported changes publish an atomic revision and recompute labels; uncertainty holds; fetch failure retains the last supported facts |
| MON-05 | Unattended operation | Scheduling, retries, idempotency and decision history prove that a change can update or hold without owner action |

After one record passes MON-01..05, extend monitoring to the remaining
published records. A failed fetch or passed deadline never deletes a record or
closes a different round. Student pages retain the last supported facts and
their actual checked date; operational warnings remain internal unless a
public claim can no longer be supported.

## Growth requirements (Stage 3)

Discover additional opportunities from permitted government, university and
approved scholarship NGO sources, extract evidence-backed candidates,
reconcile identity and duplicates, and publish through the same gates. Discovery waits for
reliable Stage 2 monitoring.

## Later features and exclusions

Profiles, personal fit assessments, saved items, comparison, checklists,
reminders and accounts are deferred. The first release collects no personal
applicant data. Automatic application submission, match scores, private-source
scraping, competitor-content copying, affiliate clutter and email capture
before content are out of scope.

## Release gates and open product decisions

Stage 1 requires a deployed no-account site with a small set of individually
source-checked records. Choose the **best-evidenced** launch records; replace
weak candidates when needed and retain all four existing fixtures as
regression inputs. The final count follows evidence quality, not a four-record
quota. Every launched record must pass the policy; a held record cannot be
published to meet a count.
Build and test the public UI with development-only data while source checking
is implemented; that data must never appear as published in production.
Stage 2 requires one unattended unchanged/safe-change/conflict/fetch-failure
demonstration with last-supported-version behaviour.

Before launch, settle and verify: CGRS D's absence of stated
tuition coverage; RMIT's actual fee-offset scope; whether UdeM's exemption
covers full tuition or only supplemental charges; each research-degree level;
real domain, organisation/contact details, and whether “no paid listings or
sponsored placement” is true. Do not publish that business-model claim until
confirmed. If requirements and application destinations are identical, show
one action. The example card must use a record that passes publication and
must not imply unsupported funding coverage.
