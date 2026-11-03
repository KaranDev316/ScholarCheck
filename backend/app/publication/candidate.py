"""Candidate extraction: an extraction pass's proposal, checked before use.

The extraction pass proposes a record and a reading for every decision-critical
field. This module turns that proposal into an ``ExtractedCandidate``: it
refuses a reading whose evidence entry, snapshot or quoted span does not line
up, and it derives each fact's state from the readings themselves — one agreed
value is ``stated``, no reading plus a stated reason is ``unspecified``, and
readings that disagree are ``conflicting``.

Extraction is deliberately not allowed to decide support. It says what the
pages say; the separate evidence check (``evidence_check.py``) decides whether
that supports the claim, and the gate decides publication.
"""

from collections.abc import Mapping

from pydantic import Field, model_validator

from app.domain.hashing import content_hash
from app.domain.models import DomainModel, Evidence, Identifier, Opportunity
from app.publication.contracts import SourceSnapshot
from app.publication.facts import (
    FactReading,
    FactState,
    MaterialFact,
    MaterialFactKind,
    MaterialFacts,
    Subject,
    normalise,
    required_fact_keys,
)
from app.publication.gates import digits_only, excerpt_in_text


class ExtractionRefused(ValueError):
    """Raised when a proposal cannot be turned into a checked candidate."""


class ReadingProposal(DomainModel):
    """One proposed reading: a value and the exact span that states it."""

    value: str = Field(min_length=1, max_length=400)
    evidence_id: Identifier
    snapshot_id: Identifier
    excerpt: str = Field(min_length=1)


class FactProposal(DomainModel):
    """A proposed fact: its readings, or a reason no reading exists."""

    kind: MaterialFactKind
    subject: Subject
    readings: tuple[ReadingProposal, ...] = ()
    reason: str | None = None

    @property
    def key(self) -> str:
        return f"{self.subject}.{self.kind.value}"


class ExtractionProposal(DomainModel):
    """The whole output of one extraction pass over one source or page set."""

    opportunity: Opportunity
    facts: tuple[FactProposal, ...] = ()

    @model_validator(mode="after")
    def one_proposal_per_field(self) -> "ExtractionProposal":
        keys = [fact.key for fact in self.facts]
        repeated = sorted({key for key in keys if keys.count(key) > 1})
        if repeated:
            raise ValueError("one reading per field; repeated: " + ", ".join(repeated))
        return self


class ExtractedCandidate(DomainModel):
    """A proposed record with its material facts, ready for the evidence check."""

    opportunity: Opportunity
    facts: MaterialFacts

    @property
    def content_hash(self) -> str:
        """The hash of the proposed record, which a report must name."""

        return content_hash(self.opportunity)

    @property
    def missing_fact_keys(self) -> tuple[str, ...]:
        """Facts the record obliges that the extraction pass did not record."""

        required = required_fact_keys(self.opportunity)
        return tuple(key for key in required if self.facts.find(key) is None)


def extract_candidate(
    proposal: ExtractionProposal,
    snapshots: Mapping[str, SourceSnapshot],
) -> ExtractedCandidate:
    """Check a proposal against its retained snapshots and derive fact states."""

    record = proposal.opportunity
    evidence_by_id = {entry.id: entry for entry in record.evidence}
    subjects = _subject_index(record)
    facts = tuple(
        _build_fact(proposed, evidence_by_id, snapshots, subjects)
        for proposed in proposal.facts
    )
    return ExtractedCandidate(opportunity=record, facts=MaterialFacts(facts=facts))


def _subject_index(record: Opportunity) -> dict[str, object]:
    """Every subject a fact may name, mapped to the part of the record it is."""

    index: dict[str, object] = {"record": record}
    for programme in record.programmes:
        index[f"programme:{programme.id}"] = programme
    for round_entry in record.rounds:
        index[f"round:{round_entry.id}"] = round_entry
    for component in record.funding_components:
        index[f"component:{component.id}"] = component
    for rule in record.eligibility_rules:
        index[f"rule:{rule.id}"] = rule
    return index


def _build_fact(
    proposed: FactProposal,
    evidence_by_id: Mapping[str, Evidence],
    snapshots: Mapping[str, SourceSnapshot],
    subjects: Mapping[str, object],
) -> MaterialFact:
    label = proposed.key
    if proposed.subject not in subjects:
        raise ExtractionRefused(
            f"{label}: the record has no {proposed.subject.split(':')[0]} "
            f"called {proposed.subject.split(':')[-1]}"
        )

    readings = tuple(
        _build_reading(label, proposed.kind, reading, evidence_by_id, snapshots)
        for reading in proposed.readings
    )
    values = {normalise(reading.value) for reading in readings}

    if not readings:
        if not proposed.reason:
            raise ExtractionRefused(
                f"{label}: a field with no reading must say why the source does not state it"
            )
        return MaterialFact(
            kind=proposed.kind,
            subject=proposed.subject,
            state=FactState.UNSPECIFIED,
            reason=proposed.reason,
        )
    if len(values) == 1:
        return MaterialFact(
            kind=proposed.kind,
            subject=proposed.subject,
            state=FactState.STATED,
            value=readings[0].value,
            readings=readings,
        )
    if not proposed.reason:
        raise ExtractionRefused(
            f"{label}: the readings disagree; record what conflicts instead of picking one"
        )
    return MaterialFact(
        kind=proposed.kind,
        subject=proposed.subject,
        state=FactState.CONFLICTING,
        readings=readings,
        reason=proposed.reason,
    )


def _build_reading(
    label: str,
    kind: MaterialFactKind,
    reading: ReadingProposal,
    evidence_by_id: Mapping[str, Evidence],
    snapshots: Mapping[str, SourceSnapshot],
) -> FactReading:
    snapshot = snapshots.get(reading.snapshot_id)
    if snapshot is None:
        raise ExtractionRefused(
            f"{label}: snapshot {reading.snapshot_id} was not retained"
        )
    evidence = evidence_by_id.get(reading.evidence_id)
    if evidence is None:
        raise ExtractionRefused(
            f"{label}: the record carries no evidence entry {reading.evidence_id}"
        )
    if str(evidence.url) != str(snapshot.url):
        raise ExtractionRefused(
            f"{label}: {reading.evidence_id} and its snapshot are different pages"
        )
    if evidence.retrieved_at != snapshot.retrieved_at:
        raise ExtractionRefused(
            f"{label}: the snapshot was retrieved at a different time"
        )
    if not excerpt_in_text(snapshot.body, reading.excerpt):
        raise ExtractionRefused(
            f"{label}: the quoted span is not in the retained snapshot"
        )
    if kind is MaterialFactKind.AMOUNT:
        wanted = digits_only(reading.value)
        if not wanted or wanted not in digits_only(reading.excerpt):
            raise ExtractionRefused(
                f"{label}: the reading states {reading.value!r}, which its quote does not"
            )
    return FactReading(
        value=reading.value,
        evidence_id=reading.evidence_id,
        snapshot_id=reading.snapshot_id,
        excerpt=reading.excerpt,
    )


__all__ = [
    "ExtractedCandidate",
    "ExtractionProposal",
    "ExtractionRefused",
    "FactProposal",
    "ReadingProposal",
    "extract_candidate",
]
