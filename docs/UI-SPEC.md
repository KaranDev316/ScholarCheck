# UI-SPEC.md — ScholarCheck public UI

> Derived from `CONTEXT.md`, `PRP.md` and `ROADMAP.md`. **If this file conflicts with `PRP.md`, `PRP.md` wins.**
> Tokens live in `frontend/src/styles/tokens.css`. Scope: first release (Stage 1) — Home, Find scholarships, Scholarship page.

## 1. Design goals

Within 5 seconds of opening any card, a student can answer:
1. **What is it, and who gives it?** Provider, country, title.
2. **What do I actually get?** One named component (e.g. "Annual stipend") with amount and currency.
3. **Can I trust it?** Source, check date, and unknowns shown honestly.

The UI never decides eligibility, ranks scholarships or shows a score. It shows official wording and makes gaps visible.

## 2. Hard rules from PRP (do not violate)

| Rule | Detail |
|---|---|
| No human-verification label | Use "Matches the official page", source and check date instead |
| No email capture, accounts, saved items, theme switch, preview banner, "How we check" page | Out of first release |
| Unknowns use an amber hatched "Not specified" treatment | Must be visibly different from positive facts |
| "Fully funded" chip | Computed; only when official evidence establishes tuition, living costs **and** flights |
| Never sum, convert or rank amounts across currencies | Every headline amount names its component and basis |
| A date without a year never implies an open round | Passed date labelled "Date passed", affecting only its own round |
| Gold is for primary actions, thin rules and the "Fully funded" chip | Never body text on off-white |
| Focus outlines are navy | Light ring on navy surfaces so it stays visible |
| Do not publish "no paid listings or sponsored placement" | Until confirmed |
| Student copy omits claim counts, policy version, revision number, gate explanations | Internal only |
| Development data must never look published | Clearly marked in dev, absent in production |

## 3. Tokens (summary — full values in `tokens.css`)

- **Colours:** navy `#0D173B`, off-white `#F8F9FA`, gold `#D4AF37`, white cards. Dark theme follows `prefers-color-scheme`; no toggle.
- **Type:** headings Iowan Old Style / Charter / Georgia; body system sans. Scale 14/16/18/22/28/40; hero 40→52px with `text-wrap: balance`.
- **Spacing:** 4px base (4, 8, 12, 16, 24, 32, 48, 64). Radius: card 12, button 8, chip pill.
- **Targets:** min tap 44×44px. Content max 1120px, reading width 720px.
- **Contrast:** text ≥4.5:1, UI borders ≥3:1, checked in both themes.

## 4. Components

### Header
Navy, 2px gold bottom rule, wordmark left, **Home** and **Find scholarships** right. Active link has a filled state, not colour alone.

### Search
One input + gold Search button. Placeholder: "Try 'doctoral scholarships in Canada'". Matches title and provider; "doctoral"/"doctorate" map to PhD. Enter submits and navigates to Find scholarships with the query in the URL.

### Filter chips (Country, Level, Funding type)
- Level: Bachelor's, Master's, PhD. "Research degree" only as a fallback when the source doesn't distinguish.
- Funding type, in order: Fully funded, Tuition + stipend, Tuition.
- Toggle buttons with `aria-pressed`. Selected = gold fill + navy text + check mark.
- Active filters appear as removable chips ("PhD ✕") plus "Clear filters".

### Scholarship card (top to bottom)
1. Provider · Country (muted, small)
2. Title (serif, max 2 lines)
3. Tags: level(s) and funding type. Show a funding tag only when the source establishes it; never show "Funding type not established".
4. Headline component: **label first**, then amount, e.g. "Annual stipend" / "CAD $40,000" / "per year for 36 months". If currency isn't stated, show a smaller amount and "Currency not stated" in muted text, never in the large number.
5. "Source checked 3 Nov 2026" (actual checked date)
6. One action: **See scholarship details** (filled gold button)

### Coverage checklist
Rows: Tuition, Living costs, Flights. Each is **Covered** (check + text) or **Not stated** (amber hatch, dark text, info icon, title "The official source doesn't say"). When several are unknown on a compact surface (e.g. the hero example), collapse them into one line: "Not stated by provider: tuition, living costs, flights".

### Evidence block
Exact retained passage in quote style, source link to the provider's page, saved date, result "Matches the official page". Max width 720px.

### Round / date / status table
Columns: Round · Date · Status. Status: Open, Date passed, Not announced, Check with institution. Wide tables scroll inside their own container.

### Official actions
"Read the requirements" and "Apply on the provider's site" appear as two buttons only when they lead to different confirmed destinations; otherwise one. If the date has passed or the route is unavailable, show a plain explanation, never a misleading disabled button. On phones the primary action sticks to the bottom.

### Share and report
Text-labelled **Copy link** and **Share** using the canonical URL. "See something wrong?" opens a dialog: focus trap, Esc closes, returns focus to trigger, clear success/error message, abuse controls handled by the endpoint.

## 5. Screens

### Home
1. **Navy hero** (two columns desktop, stacked mobile). Left: headline "Find funding. Check the evidence. Decide for yourself." (one sentence per line on desktop), one sentence about official wording, search, "No account needed." Right: one real evidence-backed example card that does not imply unsupported coverage.
2. **Quick filters** directly under the hero, above the fold. Selecting one goes to Find scholarships with it applied.
3. **Published scholarships** grid: 1 / 2 / 3 columns, left-aligned, not stretched when few.
4. **Footer** (navy, gold top rule): disclaimer "ScholarCheck shows what official sources say. It is not an eligibility decision and does not predict awards. Confirm details with the provider before applying." Real contact details when available.

No pipeline explainer, stats row, or "Browse all N" count link.

### Find scholarships
Search + filters at top, active chip row, heading "N scholarships" (singular for 1), card grid.
- **Loading:** skeleton cards
- **Error:** plain message + Retry
- **Empty:** "No published scholarships match these filters." + Clear filters

### Scholarship page
1. Breadcrumb: Find scholarships › Title
2. Title, provider, country, level tags, Copy link, Share
3. Summary strip: headline component, amount and basis, checked date, funding tag
4. Official actions
5. Coverage checklist, then separate funding components
6. Stated eligibility with: "These are the provider's stated requirements, not a decision about you."
7. Round / date / status table
8. Exact evidence
9. Navy source-check panel (source, check date, result)
10. At-a-glance facts
11. "See something wrong?"

Unknown IDs show the agreed 404.

## 6. Copy rules

- Dates: **3 Nov 2026** everywhere (avoids dd/mm vs mm/dd confusion).
- One wording per context: "Not stated" in the coverage checklist, "Not specified" in facts.
- 3-line summary first (**Who it's for · What it covers · When**), nuance in a "Details" expander or the evidence block.
- Say "source check", never internal pipeline terms.

## 7. Accessibility and quality

- Full keyboard operation; visible focus in both themes
- Labelled inputs; outcomes conveyed by text/icon, never colour alone
- Responsive from 360px, no horizontal page scroll
- Respect `prefers-reduced-motion`
- Loading, error and empty states driven by real API state

## 8. Acceptance checklist

- [ ] Hero headline breaks into three clean lines on desktop
- [ ] No amount without a named component and basis
- [ ] No "(currency not stated)" in large type; one currency presentation everywhere (hero, card, detail)
- [ ] No gold text on off-white or on the hatch
- [ ] Filters visible above the fold on Home
- [ ] Selected chips obvious without colour
- [ ] Every date reads "3 Nov 2026"
- [ ] "Fully funded" only when all three coverage items are Covered
- [ ] Unknowns use amber hatch with readable text (≥4.5:1)
- [ ] Light and dark themes both pass contrast and focus checks
- [ ] Development data never looks published
- [ ] No human-verification label, email capture, or unconfirmed business-model claim

## 9. Implementation order for the coding AI

1. Import `tokens.css`; replace hard-coded colours, sizes and spacing
2. Shared components: Card, FilterChip, CoverageChecklist, UnknownBadge, DateRoundTable, EvidenceBlock, ActionBar
3. Home → Find scholarships → Scholarship page
4. States and accessibility pass

Do not change backend contracts, add packages or refactor unrelated code. Run typecheck, lint and tests after each step.
