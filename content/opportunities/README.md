# Seed content — format v1

One file per opportunity: `content/opportunities/<opportunity-id>.yaml`. The
file contains exactly one `Opportunity` object (no wrapper, no metadata block),
so it validates directly against `backend/app/domain/models.py` and a typo fails
loudly instead of disappearing (`extra="forbid"`).

Validate the whole directory:

```bash
cd backend && .venv/bin/python -m pytest tests/test_seed_content.py
```

## Rules

1. **Keys** are the Python field names in `backend/app/domain/models.py`
   (`snake_case`). The API re-emits them in `camelCase`; the YAML never uses
   camelCase.
2. **Ids** are stable lower-case slugs (`^[a-z0-9]+(?:-[a-z0-9]+)*$`). Evidence
   ids start with `ev-`. Ids must be unique within a file, across rules, funding
   components and evidence.
3. **Amounts** are quoted decimal strings with a dot decimal separator and no
   thousands separator (`"36245"`, `"24067.80"`). `currency` is an ISO 4217 code
   and is only present when `amount` is present (`"24 067,80 $"` in a French
   source becomes `"24067.80"` plus `currency: CAD`).
4. **Periods and conditions** keep the source's own wording where it is short
   (`per year`, `one-off`, `for the duration of the stipend`). Never convert a
   period into a different unit, and never multiply an amount out.
5. **Evidence** is required for every claim. `passage` is the supporting text
   from the page and must be a span of the retained snapshot's text, verbatim
   (`content/snapshots/`); `url` is the page it came from; `retrieved_at` is
   when that page was fetched and must include a timezone and equal the
   snapshot's `retrievedAt`, because the gate compares the two. Every evidence
   entry must be referenced by a rule or funding component, except the entry
   that backs a published date in a round label (`Round` has no reference field
   in S01); such an entry must quote a deadline.
6. **No human-verification field.** Format v1 seeds carry no `verified_at`,
   `verified_by` or `last_verified_at`; those fields are gone from the model.
   Whether a record may be public is decided only by the publication gate,
   which needs a validation report and the retained snapshots that report
   checked (`docs/PUBLICATION-POLICY.md`). A fetch or YAML validation test
   alone is still insufficient. The open findings for each fixture live in
   `content/publication/first-pass-review.json`, which the gate reads itself: a
   fixture with an entry there stays held until that entry is removed after a
   re-check.
7. **No invention.** If the source does not state a fact, omit the field. A
   funding component whose value is not stated stays on the record with
   `status: unspecified` and no `amount`/`currency`; it is never shown as zero,
   as free, or as full coverage. Components are never summed.
8. **Presence is not a claim.** Nothing in a seed file asserts that an absent
   component (for example tuition for an enrolment-only award) is unavailable;
   absence only means the source says nothing.
9. **Blocking rules** (`blocking: true`) are reserved for conditions the source
   states exclude an applicant. Competition or priority statements are
   `blocking: false`.
10. **Summaries and requirement text are our own words.** `scheme_name` and
    `funder` are the provider's; passages are exact quotations from the retained
    snapshot; `summary` and `requirement` are written by us.
11. **Rounds carry identity only** in S01 (`label`, `intake`, `route`). Deadline
    *status* logic belongs to S02; published dates may appear inside `label` and
    in evidence, not as computed fields.
12. **Table passages** preserve the labels and cells in their retained-text
    order. A passage must occur in the saved snapshot after whitespace
    normalisation; explanatory table transcriptions are not exact quotations.

## Fixture register

All four now cite official-source snapshots retrieved on 2026-11-02. Their
passages and retrieval times match those retained artifacts. **None is
source-checked for publication.** The historical
[first-pass review](../../docs/slices/S01/FIRST-PASS-REVIEW.md) led to fixture
corrections; the unresolved RMIT round remains in the
[findings register](../publication/first-pass-review.json).

| File | Covers | Official sources |
|---|---|---|
| `cgsd-doctoral.yaml` | Enrolment-only doctoral award; award use is not classified | [NSERC CGRS D](https://nserc-crsng.canada.ca/en/funding-opportunity/canada-graduate-research-scholarship-doctoral-program) |
| `udem-exemption-doctoral.yaml` | Tuition exemption, tuition reduction not stipend | [UdeM exemption](https://registraire.umontreal.ca/droits-de-scolarite/bourse-exemption/), [ESP funding](https://esp.umontreal.ca/financement/) |
| `rmit-research-stipend.yaml` | Multi-stage EOI round, stipend plus international tuition offset | [RMIT scholarships](https://www.rmit.edu.au/research/research-degrees/scholarships), [RMIT stipend](https://www.rmit.edu.au/scholarships/research/research-stipend), [RMIT T&Cs](https://www.rmit.edu.au/research/research-degrees/terms-and-conditions) |
| `usyd-rtp-stipend.yaml` | Stipend plus fee offset, separate components | [RTP overview](https://www.sydney.edu.au/scholarships/australian-government-research-training-program.html), [RTP international](https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html) |

## Future publication migration

Keep these four files as regression inputs. Move material facts into the new
stated/unspecified/conflicting contract and link them to retained official
snapshots. The legacy human-verification fields are already gone. Candidates
with missing or conflicting material evidence remain held.
