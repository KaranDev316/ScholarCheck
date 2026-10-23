# ROADMAP.md — Scholarship MVP, then reliable monitoring

Inputs: `CONTEXT.md`, `PRP.md`, `PUBLICATION-POLICY.md`. Owner decision D-10
(23 October 2026) sets the sequence below. The four current fixtures are
unpublished development data until their material claims pass the publication
policy.

## Stage 1 — Make it work (finish S01)

Publish the four existing scholarships with source-backed evidence and a
usable public website. No account is required.

| Order | Deliverable | Exit proof |
|---|---|---|
| 1 | Resolve the four fixture issues in `slices/S01/FIRST-PASS-REVIEW.md` and retain the official-source content used for each decision | Every displayed material claim points to a retained passage or table cell; ambiguous or unsupported claims are removed, qualified, or held |
| 2 | Finish the validation and publication path | All required gates in `PUBLICATION-POLICY.md` pass before a record becomes public; failed records remain private; decisions and revision metadata are stored |
| 3 | Complete list, search, filter and detail APIs for published opportunities | Only published records appear publicly; country, study level and funding filters work; unknown IDs return the agreed 404 |
| 4 | Build the public site | Visitors can browse/search, filter, read eligibility, deadlines and evidence, open official application links, and share direct scholarship URLs without signing in |
| 5 | Run release checks and deploy | Four source-checked records are public, all first-release journeys work at the deployed URL, and provenance and freshness are understandable |

The four records are a target, not a reason to bypass a failed gate. If a
source cannot support a material claim, hold that record and report the release
gap. Human review is optional and cannot be silently represented by an agent.

## Stage 2 — Make it update itself

Monitor **one** of the published scholarships first. Fetch its registered
official source on a schedule, retain an immutable snapshot, and compare it to
the last checked version. Unchanged content does no publication work. A
meaningful change creates a candidate that runs through the same evidence and
validation gates as initial publication.

The worker either publishes an explained revision or holds it with a reason.
Fetch failures and uncertain changes keep the last-known-good public record
and show its recheck state. Retries, duplicate processing and audit history
must be tested. This stage is complete when a material change is detected,
validated, and safely updated or held without owner intervention.

After that proof, extend monitoring to the other three published records.

## Stage 3 — Make it grow itself

Add official-source discovery, extraction of new candidates, identity and
duplicate reconciliation, and automatic publication through the existing
gates. Expand beyond the four records only after Stage 2 is reliable.

## Deferred from the first release

Applicant profiles and personal eligibility assessments, saved items,
comparison, checklists, notifications, accounts, and catalogue-size targets
remain later work. The first release displays **stated eligibility**; it does
not decide whether a particular visitor qualifies. Automatic application
submission and match probabilities remain out of scope.

## Current implementation

The React/FastAPI scaffold, four YAML fixtures, PostgreSQL loader, and a
development-only detail read endpoint exist. The publication engine, public
list/search API, public listing UI and source monitor do not yet exist. The
S01 evidence ledger records completed checks and outstanding proof.
