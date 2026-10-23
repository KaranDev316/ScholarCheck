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
   from the page; `url` is the page it came from; `retrieved_at` is when the page
   was fetched and must include a timezone. Every evidence entry must be
   referenced by a rule or funding component, except the entry that backs a
   published date in a round label (`Round` has no reference field in S01); such
   an entry must quote a deadline.
6. **Verification is separate from retrieval.** Seeds ship with
   `verified_at: null`, `verified_by: null` and `last_verified_at: null`. Only a
   human who has opened the official page sets those, and
   `VERIFICATION.md` A2 requires that before release. An automatic refresh may
   change `retrieved_at`; it must never set `verified_at`.
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
10. **Summaries and requirement text are our own words.** `scheme_name`,
    `funder` and passages are quoted or transcribed; `summary` is written by us.
11. **Rounds carry identity only** in S01 (`label`, `intake`, `route`). Deadline
    *status* logic belongs to S02; published dates may appear inside `label` and
    in evidence, not as computed fields.
12. **Table transcriptions** (pages whose content is a table) are marked
    `[Table, transcribed]` at the start of the passage. Cell labels are kept and
    columns are separated by `;`, so a reviewer can re-read the table cell by
    cell.

## Fixture register

All four were retrieved on 2026-10-23. **None is human-verified yet**
(`verified_at` is null on every evidence entry), so A2 remains open.

| File | Covers | Official sources |
|---|---|---|
| `cgsd-doctoral.yaml` | Enrolment-only doctoral award, living support only | [NSERC CGRS D](https://www.nserc-crsng.gc.ca/students-etudiants/pg-cs/cgsd-bescd_eng.asp) |
| `udem-exemption-doctoral.yaml` | Tuition exemption, tuition reduction not stipend | [UdeM exemption](https://registraire.umontreal.ca/droits-de-scolarite/bourse-exemption/), [ESP funding](https://esp.umontreal.ca/financement/) |
| `rmit-research-stipend.yaml` | Multi-stage EOI round, stipend plus international tuition offset | [RMIT scholarships](https://www.rmit.edu.au/research/research-degrees/scholarships), [RMIT stipend](https://www.rmit.edu.au/scholarships/research/research-stipend), [RMIT T&Cs](https://www.rmit.edu.au/research/research-degrees/terms-and-conditions) |
| `usyd-rtp-stipend.yaml` | Stipend plus fee offset, separate components | [RTP overview](https://www.sydney.edu.au/scholarships/australian-government-research-training-program.html), [RTP international](https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html) |

## Verification checklist for a human reviewer

For each evidence entry: open `url`, confirm `passage` appears on the page (or
that the table transcription matches cell by cell), then set `verified_at`,
`verified_by` and the record's `last_verified_at`. If a claim has changed,
update the value and the passage, and report the change rather than silently
overwriting it.
