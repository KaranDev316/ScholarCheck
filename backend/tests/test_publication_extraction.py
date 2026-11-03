"""The extraction pass proposes; this module refuses and derives (T06).

Extraction says what the pages say. It never decides support: a fact it cannot
back with a retained snapshot and an exact span is refused here, and an amount
whose quote does not contain those digits never reaches the gate.
"""

from datetime import timedelta

import pytest
from pydantic import ValidationError

from app.domain.hashing import content_hash
from app.domain.models import Evidence, Opportunity
from app.publication.candidate import (
    ExtractedCandidate,
    ExtractionProposal,
    ExtractionRefused,
    FactProposal,
    ReadingProposal,
    extract_candidate,
)
from app.publication.facts import FactState, MaterialFactKind, subject
from tests.publication_helpers import (
    RETRIEVED_AT,
    SAMPLE_PASSAGE,
    SAMPLE_URL,
    build_snapshots,
    sample_record,
    snapshot_id,
)

AMOUNT = MaterialFactKind.AMOUNT
RATE_YEAR = MaterialFactKind.RATE_YEAR


def amount_reading(
    value: str = "40000",
    *,
    evidence_id: str = "ev-value",
    snapshot: str | None = None,
    excerpt: str = SAMPLE_PASSAGE,
) -> ReadingProposal:
    return ReadingProposal(
        value=value,
        evidence_id=evidence_id,
        snapshot_id=snapshot or snapshot_id(SAMPLE_URL),
        excerpt=excerpt,
    )


def amount_fact(*readings: ReadingProposal, reason: str | None = None) -> FactProposal:
    return FactProposal(
        kind=AMOUNT,
        subject=subject("component", "fund-living"),
        readings=readings,
        reason=reason,
    )


def extract(
    *facts: FactProposal, record: Opportunity | None = None
) -> ExtractedCandidate:
    record = record if record is not None else sample_record()
    snapshots = build_snapshots(record)
    return extract_candidate(
        ExtractionProposal(opportunity=record, facts=facts),
        {snapshot.id: snapshot for snapshot in snapshots},
    )


def test_an_agreed_reading_becomes_a_stated_fact() -> None:
    candidate = extract(amount_fact(amount_reading()))
    fact = candidate.facts.find("component:fund-living.amount")

    assert fact is not None
    assert fact.state is FactState.STATED
    assert fact.value == "40000"
    assert fact.readings[0].snapshot_id == snapshot_id(SAMPLE_URL)
    assert fact.readings[0].excerpt == SAMPLE_PASSAGE


def test_a_field_with_a_reason_and_no_reading_is_unspecified() -> None:
    candidate = extract(
        FactProposal(
            kind=RATE_YEAR,
            subject=subject("component", "fund-living"),
            reason="the page gives no rate year for the stipend",
        )
    )
    fact = candidate.facts.find("component:fund-living.rate_year")

    assert fact is not None
    assert fact.state is FactState.UNSPECIFIED
    assert fact.value is None
    assert fact.readings == ()


def test_a_field_with_neither_a_reading_nor_a_reason_is_refused() -> None:
    with pytest.raises(ExtractionRefused, match="must say why"):
        extract(FactProposal(kind=RATE_YEAR, subject=subject("record")))


def test_readings_that_disagree_are_refused_unless_the_conflict_is_recorded() -> None:
    other = Evidence(
        id="ev-regulations",
        url=f"{SAMPLE_URL}/regulations",
        passage="The stipend is paid at $41,000 per year.",
        retrieved_at=RETRIEVED_AT,
    )
    record = sample_record(evidence=(*sample_record().evidence, other))
    readings = (
        amount_reading(),
        amount_reading(
            "41000",
            evidence_id="ev-regulations",
            snapshot=snapshot_id(f"{SAMPLE_URL}/regulations"),
            excerpt=other.passage,
        ),
    )

    with pytest.raises(ExtractionRefused, match="record what conflicts"):
        extract(amount_fact(*readings), record=record)

    conflicting = amount_fact(*readings, reason="the two pages disagree")
    fact = extract(conflicting, record=record).facts.find(
        "component:fund-living.amount"
    )

    assert fact is not None
    assert fact.state is FactState.CONFLICTING
    assert fact.value is None
    assert fact.evidence_refs == ("ev-value", "ev-regulations")


def test_a_quote_the_retained_snapshot_does_not_contain_is_refused() -> None:
    with pytest.raises(ExtractionRefused, match="not in the retained snapshot"):
        extract(amount_fact(amount_reading(excerpt="The scholarship pays $40,000.")))


def test_evidence_and_snapshot_from_different_pages_are_refused() -> None:
    other = Evidence(
        id="ev-regulations",
        url=f"{SAMPLE_URL}/regulations",
        passage=SAMPLE_PASSAGE,
        retrieved_at=RETRIEVED_AT,
    )
    record = sample_record(evidence=(*sample_record().evidence, other))

    with pytest.raises(ExtractionRefused, match="different pages"):
        extract(
            amount_fact(
                amount_reading(snapshot=snapshot_id(f"{SAMPLE_URL}/regulations"))
            ),
            record=record,
        )


def test_a_snapshot_that_was_not_retained_is_refused() -> None:
    with pytest.raises(ExtractionRefused, match="was not retained"):
        extract(amount_fact(amount_reading(snapshot="snap-nowhere")))


def test_evidence_the_record_does_not_carry_is_refused() -> None:
    with pytest.raises(ExtractionRefused, match="no evidence entry ev-ghost"):
        extract(amount_fact(amount_reading(evidence_id="ev-ghost")))

def test_a_reading_whose_page_was_retrieved_at_another_time_is_refused() -> None:
    record = sample_record()
    stale = build_snapshots(record)[0].model_copy(
        update={"retrieved_at": RETRIEVED_AT - timedelta(days=1)}
    )

    with pytest.raises(ExtractionRefused, match="retrieved at a different time"):
        extract_candidate(
            ExtractionProposal(
                opportunity=record,
                facts=(amount_fact(amount_reading()),),
            ),
            {stale.id: stale},
        )


def test_an_amount_its_quote_does_not_state_is_refused() -> None:
    with pytest.raises(ExtractionRefused, match="its quote does not"):
        extract(amount_fact(amount_reading("50000")))


def test_a_reading_that_is_not_an_amount_need_not_carry_digits() -> None:
    record = sample_record(
        evidence=(
            Evidence(
                id="ev-value",
                url=SAMPLE_URL,
                passage="The stipend of $40,000 per year is paid in CAD.",
                retrieved_at=RETRIEVED_AT,
            ),
        )
    )
    candidate = extract(
        FactProposal(
            kind=MaterialFactKind.CURRENCY,
            subject=subject("component", "fund-living"),
            readings=(amount_reading(value="CAD", excerpt="paid in CAD."),),
        ),
        record=record,
    )

    assert candidate.facts.keys == ("component:fund-living.currency",)
    assert candidate.facts.stated[0].value == "CAD"


def test_a_fact_about_a_part_the_record_does_not_have_is_refused() -> None:
    with pytest.raises(ExtractionRefused, match="no component called ghost"):
        extract(
            FactProposal(
                kind=AMOUNT,
                subject=subject("component", "ghost"),
                readings=(amount_reading(),),
            )
        )


def test_the_fields_the_record_obliges_are_named_and_the_rest_reported() -> None:
    candidate = extract(amount_fact(amount_reading()))

    assert candidate.missing_fact_keys == (
        "component:fund-living.currency",
        "component:fund-living.funding_relationship",
        "component:fund-living.rate_year",
    )


def test_the_candidate_names_the_hash_a_report_must_carry() -> None:
    record = sample_record()

    candidate = extract(amount_fact(amount_reading()), record=record)

    assert candidate.content_hash == content_hash(record)
    assert candidate.opportunity.id == record.id


def test_the_proposal_refuses_two_facts_for_one_field() -> None:
    with pytest.raises(ValidationError, match="one reading per field"):
        ExtractionProposal(
            opportunity=sample_record(),
            facts=(amount_fact(amount_reading()), amount_fact(amount_reading())),
        )
