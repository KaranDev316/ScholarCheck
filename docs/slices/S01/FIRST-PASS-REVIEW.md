# S01 fixture source check — agent first pass

Checked 23 October 2026 against the linked official web pages. This is a source
comparison, **not human verification**. No `verified_at`, `verified_by`, or
`last_verified_at` field was changed. A page being reachable, or a passage
matching it, does not prove that the fixture is complete or that an applicant
qualifies.

Status key: **corroborated** = the current official page supports the recorded
claim; **change needed** = the fixture wording or route could mislead;
**unclear** = the checked page does not settle the claim. Table transcriptions
were checked against the named row and column, rather than treated as verbatim
sentences. This pass covered the four main scholarship pages, RMIT's terms and
round pages, Sydney's overview, and the linked application guidance. It did
not audit every linked PDF or every possible eligibility restriction.

## Findings needing action

| Priority | Fixture | Finding and proposed action |
|---|---|---|
| High | CGRS D | `cgsd-direct-route` and its 17 October label apply only to applicants eligible to submit directly. An international applicant at a Canadian institution **with** a doctoral award quota must submit through that institution, whose deadline may be earlier. Split or qualify the route before showing the date as the applicant's deadline. The NSERC portal link also serves only one of the three agencies; route applicants to the relevant agency's instructions. [Application and route table](https://nserc-crsng.canada.ca/en/funding-opportunity/canada-graduate-research-scholarship-doctoral-program) |
| High | RMIT | The fixture says the stipend is “pro rata for part-time study”; the source says `$36,245 per annum pro rata (full-time study)`, while the page says part-time applications are considered for **local** applicants in exceptional circumstances. Remove the part-time inference. The amount is explicitly a **2026** benefit, not a confirmed 2027 rate. [Stipend page](https://www.rmit.edu.au/scholarships/research/research-stipend) |
| High | RMIT | The 2027 **international** EOI deadline was 30 August 2026 and the full application deadline was 30 September 2026. Both precede this check date. The page still says applications are “open”, but its date table and instruction to submit by advertised deadlines do not support presenting this round as currently open. Keep the historical dates; mark availability for recheck or closed when S02 status logic arrives. [Round table](https://www.rmit.edu.au/research/research-degrees/scholarships) |
| High | Sydney | The recorded Research Period 1–2, 2027 submission deadline was 11 September 2026, already past. The same table lists Research Period 3–4, 2027 with a 18 December 2026 submission deadline. Add that as a separate round before giving users a next available deadline; admission and scholarship steps must remain distinct. [International timeline](https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html) |
| Medium | UdeM | `route: awarded automatically with admission` is too strong. The university evaluates eligible candidates during admission and applies the exemption automatically **if all conditions are met**. An admission offer alone does not guarantee an award. Qualify the route wording. [UdeM exemption](https://registraire.umontreal.ca/droits-de-scolarite/bourse-exemption/) |
| Medium | CGRS D / RMIT | The seed rules are not an exhaustive eligibility checklist. CGRS D also states restrictions on repeat applications and prior doctoral awards; RMIT adds restrictions on prior scholarships, other fee-offset awards, and prior study. Add these rules or clearly label assessments as checks of only the rules present. [CGRS D restrictions](https://nserc-crsng.canada.ca/en/funding-opportunity/canada-graduate-research-scholarship-doctoral-program), [RMIT terms](https://www.rmit.edu.au/research/research-degrees/terms-and-conditions) |
| Medium | Sydney | The `route` says “admission application, then scholarship form”, which describes **commencing** students. Currently enrolled students follow a separate path and submit the scholarship form. Qualify the route or create separate route records. [How to apply](https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html) |
| Check | CGRS D | The source states the award's value and duration, but does not explicitly call it a “living allowance” or state that tuition is excluded. Keep tuition as unstated and avoid implying the grant's permitted use is settled. The agency deadline is 17 October at 8 pm ET, with a next-business-day exception when it falls on a weekend; the source gives no year in that rule. [CGRS D page](https://nserc-crsng.canada.ca/en/funding-opportunity/canada-graduate-research-scholarship-doctoral-program) |
| Check | UdeM | The separate `requirements_url` (`esp.umontreal.ca/financement/`) could not be read through this check. The registrar page itself supports the recorded 3e-cycle rules and amount. Check whether the requirements link is still the best destination. [Registrar page](https://registraire.umontreal.ca/droits-de-scolarite/bourse-exemption/) |

## Evidence entries checked

| Fixture | Evidence ids | First-pass result |
|---|---|---|
| [CGRS D](https://nserc-crsng.canada.ca/en/funding-opportunity/canada-graduate-research-scholarship-doctoral-program) | `ev-cgsd-value`, `ev-cgsd-international`, `ev-cgsd-study-months` | Corroborated: CAD 40,000 per year for 36 months, international enrolment condition, and 36-month prior-study cap. The page does not explicitly classify the award as living costs. |
| [CGRS D](https://nserc-crsng.canada.ca/en/funding-opportunity/canada-graduate-research-scholarship-doctoral-program) | `ev-cgsd-deadline` | Corroborated as an **agency** deadline, with the route qualification and weekend exception above. Not a universal applicant deadline. |
| [UdeM](https://registraire.umontreal.ca/droits-de-scolarite/bourse-exemption/) | `ev-udem-amount`, `ev-udem-duration` | Corroborated in the **3e cycle** section: CAD 24,067.80 for 45 credits across three full-time terms in academic year 2026–2027; research doctorate exemption lasts 6–10 terms according to normal programme length. This is a reduction of supplemental tuition charges. |
| [UdeM](https://registraire.umontreal.ca/droits-de-scolarite/bourse-exemption/) | `ev-udem-eligibility`, `ev-udem-process` | Corroborated: nationality exclusions, admission offer, CAQ and permit, full-time enrolment, other exemption and external funding restrictions; no separate scholarship application. Automatic application remains conditional on eligibility. |
| [RMIT stipend](https://www.rmit.edu.au/scholarships/research/research-stipend) | `ev-rmit-stipend`, `ev-rmit-tuition`, `ev-rmit-relocation`, `ev-rmit-duration` | Corroborated for the **2026 benefit set**: AUD 36,245 annual stipend, international fee offset, relocation allowance capped at AUD 1,540, and 3.5-year standard doctoral scholarship duration. The part-time wording in the fixture needs correction. |
| [RMIT stipend](https://www.rmit.edu.au/scholarships/research/research-stipend) | `ev-rmit-english`, `ev-rmit-supervisor`, `ev-rmit-priority` | Corroborated: English requirement by closing date, supervisor support at EOI, and high distinction priority. The priority is not an outright eligibility blocker. |
| [RMIT terms](https://www.rmit.edu.au/research/research-degrees/terms-and-conditions) | `ev-rmit-enrolment`, `ev-rmit-doctorate` | Corroborated, though the referenced terms also contain additional restrictions missing from the seed. |
| [RMIT round table](https://www.rmit.edu.au/research/research-degrees/scholarships) | `ev-rmit-dates` | Corroborated in the international column: EOI opens 1 June 2026; EOI deadline 30 August 2026; full application deadline 30 September 2026. Those dates have passed. |
| [Sydney international RTP](https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html) | `ev-usyd-stipend`, `ev-usyd-tuition` | Corroborated in separate table rows: AUD 44,293 per year is the **2027** stipend rate; AUD 42,754 is the 2026 rate. RTP Fee Offset covers 100% tuition for up to 14 research periods and lists Overseas Student Health Cover; relocation and thesis allowances are listed without amounts. |
| [Sydney overview](https://www.sydney.edu.au/scholarships/australian-government-research-training-program.html) | `ev-usyd-eligibility`, `ev-usyd-academic-record`, `ev-usyd-process`, `ev-usyd-submission` | Corroborated as published preliminary requirements and application steps, with different steps for commencing and enrolled students. |
| [Sydney international timeline](https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html) | `ev-usyd-deadline` | Corroborated: 11 September 2026 for Research Period 1–2, 2027, and 18 December 2026 for Research Period 3–4, 2027. The seed currently models only the first round. |

## Automated follow-up checks

The publication pipeline must resolve: (1) the **3e-cycle** UdeM table,
conditional award wording and whether only supplemental charges are exempt;
(2) RMIT's 2026 rate, part-time wording and exact fee-offset scope; (3) the
CGRS D application channel, deadline and absent tuition statement; and (4)
Sydney's applicable research period. The four files remain regression inputs.
D-11 removes the earlier optional human-verification direction; the automatic
publication gates have not yet run.
