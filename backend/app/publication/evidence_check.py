"""The separate evidence check that turns a candidate into a validation report.

Extraction says what the pages say. This pass — and only this pass — records
whether a quoted span, read in its full context, supports the claim it is used
for: the same scholarship, applicant category, degree level, round, rate year
and application route. It never publishes: it produces a ``ValidationReport``,
and the code gate in ``gates.py`` decides what that report is worth.

The pass refuses to write a report it cannot stand behind. A verdict must be
about a material fact the candidate actually records as stated, must quote a
span that fact carries, must carry a reason when the result is not supported,
and must state the claim the span was applied to when it is supported. Every
span of every stated fact must be covered exactly once.
"""

from collections.abc import Sequence
from datetime import datetime

from pydantic import Field, model_validator

from app.domain.models import DomainModel, Identifier
from app.publication.candidate import ExtractedCandidate
from app.publication.contracts import (
    Applicability,
    CheckResult,
    ClaimCheck,
    ValidationReport,
)
from app.publication.facts import FactKey, FactState
from app.publication.policy import POLICY_VERSION


class EvidenceCheckRefused(ValueError):
    """Raised when an evidence check cannot produce an honest report."""


class Adjudication(DomainModel):
    """One verdict on one quoted span of one stated material fact.

    ``snapshot_id`` names which reading was read: a fact backed by two pages
    needs a verdict for each span, so a checker cannot support a fact from one
    page while leaving a second page that may say something else unread.
    """

    fact: FactKey
    snapshot_id: Identifier = Field(
        description="The retained snapshot whose span the checker read."
    )
    evidence_id: Identifier | None = None
    excerpt: str | None = None
    result: CheckResult
    reason: str | None = Field(
        default=None, description="Required when the result is not supported."
    )
    applies_to: Applicability | None = Field(
        default=None,
        description="The claim the span was applied to; required when supported.",
    )

    @model_validator(mode="after")
    def verdict_states_what_it_needs(self) -> "Adjudication":
        if self.result is not CheckResult.SUPPORTED:
            if not self.reason:
                raise ValueError("an unsupported or unclear verdict must state a reason")
            if self.applies_to is not None:
                raise ValueError(
                    "applicability belongs to a supported verdict, not a failed one"
                )
        elif self.applies_to is None:
            raise ValueError(
                "a supported verdict must state which claim the span applies to"
            )
        return self


def check_candidate(
    candidate: ExtractedCandidate,
    adjudications: Sequence[Adjudication],
    *,
    checked_at: datetime,
    policy_version: str = POLICY_VERSION,
) -> ValidationReport:
    """Build the validation report for one extracted candidate.

    No clock is implied: the caller supplies ``checked_at`` so a check time is
    never invented for a run that did not happen.
    """

    if checked_at.tzinfo is None:
        raise EvidenceCheckRefused("checked_at must include a timezone")

    record = candidate.opportunity
    round_ids = {round_entry.id for round_entry in record.rounds}
    degree_levels = {
        programme.degree_level for programme in record.programmes
    }
    checks: list[ClaimCheck] = []
    covered: set[tuple[str, str, str, str]] = set()

    for adjudication in adjudications:
        fact = candidate.facts.find(adjudication.fact)
        if fact is None:
            raise EvidenceCheckRefused(
                f"{adjudication.fact}: the candidate records no such material fact"
            )
        if fact.state is not FactState.STATED:
            raise EvidenceCheckRefused(
                f"{fact.key}: a {fact.state.value} fact cannot be marked "
                f"{adjudication.result.value}"
            )
        readings = [r for r in fact.readings if r.snapshot_id == adjudication.snapshot_id
                    and (adjudication.evidence_id is None or r.evidence_id == adjudication.evidence_id)
                    and (adjudication.excerpt is None or r.excerpt == adjudication.excerpt)]
        if len(readings) > 1:
            raise EvidenceCheckRefused(f"{fact.key}: multiple spans; identify evidence_id and excerpt explicitly")
        reading = readings[0] if readings else None
        if reading is None:
            raise EvidenceCheckRefused(
                f"{fact.key}: no reading of this fact comes from snapshot "
                f"{adjudication.snapshot_id}"
            )
        span = (fact.key, adjudication.snapshot_id, reading.evidence_id, reading.excerpt)
        if span in covered:
            raise EvidenceCheckRefused(
                f"{fact.key}: snapshot {adjudication.snapshot_id} was already checked"
            )
        _refuse_misplaced_claim(adjudication, round_ids, degree_levels)
        covered.add(span)
        checks.append(
            ClaimCheck(
                claim=f"{fact.kind.value.replace('_', ' ')} for {fact.subject}",
                evidence_id=reading.evidence_id,
                snapshot_id=reading.snapshot_id,
                excerpt=reading.excerpt,
                result=adjudication.result,
                reason=adjudication.reason,
                fact=fact.key,
                applies_to=adjudication.applies_to,
            )
        )

    unchecked = [
        f"{fact.key} in {reading.snapshot_id}"
        for fact in candidate.facts.stated
        for reading in fact.readings
        if (fact.key, reading.snapshot_id, reading.evidence_id, reading.excerpt) not in covered
    ]
    if unchecked:
        raise EvidenceCheckRefused("no evidence check covers: " + ", ".join(unchecked))
    if not checks:
        raise EvidenceCheckRefused(
            f"{record.id}: nothing to check; the candidate states no material fact"
        )

    return ValidationReport(
        opportunity_id=record.id,
        content_hash=candidate.content_hash,
        policy_version=policy_version,
        checked_at=checked_at,
        facts=candidate.facts,
        facts_hash=candidate.facts.fingerprint,
        snapshot_hashes=candidate.snapshot_hashes,
        checks=tuple(checks),
    )


def _refuse_misplaced_claim(
    adjudication: Adjudication,
    round_ids: set[str],
    degree_levels: set[object],
) -> None:
    """Refuse a verdict that applies a span to something the record is not."""

    applies_to = adjudication.applies_to
    if applies_to is None:
        return
    unknown = [round_id for round_id in applies_to.rounds if round_id not in round_ids]
    if unknown:
        raise EvidenceCheckRefused(
            f"{adjudication.fact}: the verdict places the quote in round "
            f"{unknown[0]}, which the record does not have"
        )
    if applies_to.degree_level is not None and applies_to.degree_level not in degree_levels:
        raise EvidenceCheckRefused(
            f"{adjudication.fact}: the verdict places the quote at degree level "
            f"{applies_to.degree_level.value}, which the record does not offer"
        )
    subject = adjudication.fact.partition(".")[0]
    if subject.startswith("round:"):
        own = subject.split(":", 1)[1]
        if applies_to.rounds and own not in applies_to.rounds:
            raise EvidenceCheckRefused(
                f"{adjudication.fact}: the quote is applied to "
                f"{', '.join(applies_to.rounds)} but states a fact about {own}"
            )


__all__ = [
    "Adjudication",
    "EvidenceCheckRefused",
    "check_candidate",
]
