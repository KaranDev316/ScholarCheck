"""The separate evidence check: what a report may and may not claim (T06).

Extraction says what the pages say; this pass records whether a span supports the
claim it is used for, and refuses to write a report it cannot stand behind. It
never publishes: the gate in ``gates.py`` decides that.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.domain.enums import DegreeLevel
from app.domain.models import Evidence, Opportunity, Round
from app.publication.candidate import (
    ExtractedCandidate,
    ExtractionProposal,
    FactProposal,
    ReadingProposal,
    extract_candidate,
)
from app.publication.contracts import Applicability, CheckResult, SourceSnapshot
from app.publication.evidence_check import (
    Adjudication,
    EvidenceCheckRefused,
    check_candidate,
)
from app.publication.facts import FactState, MaterialFactKind, subject
from app.publication.policy import POLICY_VERSION
from tests.publication_helpers import (
    CHECKED_AT,
    RETRIEVED_AT,
    SAMPLE_PASSAGE,
    SAMPLE_URL,
    build_snapshots,
    sample_record,
    snapshot_id,
)

AMOUNT_KEY = "component:fund-living.amount"
SUMMARY_PASSAGE = "A stipend of $40,000 is paid each year."


def reading(
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


def amount_fact(*readings: ReadingProposal) -> FactProposal:
    return FactProposal(
        kind=MaterialFactKind.AMOUNT,
        subject=subject("component", "fund-living"),
        readings=readings,
    )


def candidate(
    *facts: FactProposal, record: Opportunity | None = None
) -> tuple[ExtractedCandidate, dict[str, SourceSnapshot]]:
    record = record if record is not None else sample_record()
    snapshots = build_snapshots(record)
    extracted = extract_candidate(
        ExtractionProposal(opportunity=record, facts=facts),
        {snapshot.id: snapshot for snapshot in snapshots},
    )
    return extracted, {snapshot.id: snapshot for snapshot in snapshots}


def supported(key: str, snapshot: SourceSnapshot, **applies_to: object) -> Adjudication:
    options = {
        "rounds": (),
        "note": "the page states this field for this scholarship",
        **applies_to,
    }
    return Adjudication(
        fact=key,
        snapshot_id=snapshot.id,
        result=CheckResult.SUPPORTED,
        applies_to=Applicability(**options),
    )


def test_a_supported_verdict_becomes_the_report() -> None:
    extracted, snapshots = candidate(amount_fact(reading()))
    snapshot = snapshots[snapshot_id(SAMPLE_URL)]

    report = check_candidate(
        extracted, [supported(AMOUNT_KEY, snapshot)], checked_at=CHECKED_AT
    )

    assert report.opportunity_id == extracted.opportunity.id
    assert report.content_hash == extracted.content_hash
    assert report.policy_version == POLICY_VERSION
    assert report.checked_at == CHECKED_AT
    assert report.facts == extracted.facts
    assert len(report.checks) == 1
    check = report.checks[0]
    assert check.fact == AMOUNT_KEY
    assert check.evidence_id == "ev-value"
    assert check.excerpt == SAMPLE_PASSAGE
    assert check.applies_to is not None


def test_a_check_time_without_a_timezone_is_refused() -> None:
    extracted, snapshots = candidate(amount_fact(reading()))

    with pytest.raises(EvidenceCheckRefused, match="must include a timezone"):
        check_candidate(
            extracted,
            [supported(AMOUNT_KEY, snapshots[snapshot_id(SAMPLE_URL)])],
            checked_at=datetime(2026, 10, 31, 9, 0),
        )


def test_a_verdict_about_a_field_the_candidate_never_recorded_is_refused() -> None:
    extracted, snapshots = candidate(amount_fact(reading()))

    with pytest.raises(EvidenceCheckRefused, match="records no such material fact"):
        check_candidate(
            extracted,
            [
                supported(
                    "component:fund-living.rate_year",
                    snapshots[snapshot_id(SAMPLE_URL)],
                )
            ],
            checked_at=CHECKED_AT,
        )


def test_a_verdict_about_an_unspecified_field_is_refused() -> None:
    extracted, snapshots = candidate(
        amount_fact(reading()),
        FactProposal(
            kind=MaterialFactKind.RATE_YEAR,
            subject=subject("component", "fund-living"),
            reason="the page gives no rate year",
        ),
    )

    with pytest.raises(EvidenceCheckRefused, match="unspecified fact cannot be marked"):
        check_candidate(
            extracted,
            [
                supported(AMOUNT_KEY, snapshots[snapshot_id(SAMPLE_URL)]),
                supported(
                    "component:fund-living.rate_year",
                    snapshots[snapshot_id(SAMPLE_URL)],
                ),
            ],
            checked_at=CHECKED_AT,
        )


def test_a_verdict_from_a_page_the_fact_does_not_come_from_is_refused() -> None:
    extracted, snapshots = candidate(amount_fact(reading()))
    snapshot = snapshots[snapshot_id(SAMPLE_URL)]
    elsewhere = snapshot.model_copy(update={"id": "snap-elsewhere"})

    with pytest.raises(EvidenceCheckRefused, match="no reading of this fact"):
        check_candidate(
            extracted, [supported(AMOUNT_KEY, elsewhere)], checked_at=CHECKED_AT
        )


def test_a_stated_span_nobody_checked_is_refused() -> None:
    summary = Evidence(
        id="ev-summary",
        url=f"{SAMPLE_URL}/summary",
        passage=SUMMARY_PASSAGE,
        retrieved_at=RETRIEVED_AT,
    )
    record = sample_record(evidence=(*sample_record().evidence, summary))
    extracted, snapshots = candidate(
        amount_fact(
            reading(),
            reading(
                evidence_id="ev-summary",
                snapshot=snapshot_id(f"{SAMPLE_URL}/summary"),
                excerpt=SUMMARY_PASSAGE,
            ),
        ),
        record=record,
    )

    with pytest.raises(EvidenceCheckRefused, match="no evidence check covers"):
        check_candidate(
            extracted,
            [supported(AMOUNT_KEY, snapshots[snapshot_id(SAMPLE_URL)])],
            checked_at=CHECKED_AT,
        )


def test_a_second_verdict_on_the_same_span_is_refused() -> None:
    extracted, snapshots = candidate(amount_fact(reading()))
    verdict = supported(AMOUNT_KEY, snapshots[snapshot_id(SAMPLE_URL)])

    with pytest.raises(EvidenceCheckRefused, match="was already checked"):
        check_candidate(extracted, [verdict, verdict], checked_at=CHECKED_AT)


def test_a_failed_verdict_must_state_a_reason() -> None:
    with pytest.raises(ValidationError, match="must state a reason"):
        Adjudication(
            fact=AMOUNT_KEY,
            snapshot_id=snapshot_id(SAMPLE_URL),
            result=CheckResult.UNCLEAR,
        )


def test_a_failed_verdict_cannot_claim_applicability() -> None:
    with pytest.raises(ValidationError, match="belongs to a supported verdict"):
        Adjudication(
            fact=AMOUNT_KEY,
            snapshot_id=snapshot_id(SAMPLE_URL),
            result=CheckResult.UNSUPPORTED,
            reason="the page states a different amount",
            applies_to=Applicability(note="the page states this field"),
        )


def test_a_supported_verdict_must_say_which_claim_it_applies_to() -> None:
    with pytest.raises(ValidationError, match="which claim the span applies to"):
        Adjudication(
            fact=AMOUNT_KEY,
            snapshot_id=snapshot_id(SAMPLE_URL),
            result=CheckResult.SUPPORTED,
        )


def test_a_verdict_placed_in_a_round_the_record_lacks_is_refused() -> None:
    extracted, snapshots = candidate(amount_fact(reading()))

    with pytest.raises(EvidenceCheckRefused, match="which the record does not have"):
        check_candidate(
            extracted,
            [
                supported(
                    AMOUNT_KEY,
                    snapshots[snapshot_id(SAMPLE_URL)],
                    rounds=("round-ghost",),
                )
            ],
            checked_at=CHECKED_AT,
        )


def test_a_verdict_at_a_degree_level_the_record_does_not_offer_is_refused() -> None:
    extracted, snapshots = candidate(amount_fact(reading()))

    with pytest.raises(EvidenceCheckRefused, match="which the record does not offer"):
        check_candidate(
            extracted,
            [
                supported(
                    AMOUNT_KEY,
                    snapshots[snapshot_id(SAMPLE_URL)],
                    degree_level=DegreeLevel.DOCTORAL,
                )
            ],
            checked_at=CHECKED_AT,
        )


def test_a_round_fact_applied_to_another_round_is_refused() -> None:
    round_passage = "The 2027 round opens in September 2027."
    record = sample_record(
        evidence=(
            Evidence(
                id="ev-value",
                url=SAMPLE_URL,
                passage=f"{SAMPLE_PASSAGE} {round_passage}",
                retrieved_at=RETRIEVED_AT,
            ),
        )
    ).model_copy(
        update={
            "rounds": (
                Round(id="round-2027", label="2027 entry"),
                Round(id="round-2028", label="2028 entry"),
            )
        }
    )
    extracted, snapshots = candidate(
        FactProposal(
            kind=MaterialFactKind.INTAKE,
            subject=subject("round", "round-2027"),
            readings=(
                reading(value="2027", excerpt=round_passage),
            ),
        ),
        record=record,
    )

    with pytest.raises(EvidenceCheckRefused, match="states a fact about round-2027"):
        check_candidate(
            extracted,
            [
                supported(
                    "round:round-2027.intake",
                    snapshots[snapshot_id(SAMPLE_URL)],
                    rounds=("round-2028",),
                )
            ],
            checked_at=CHECKED_AT,
        )


def test_a_candidate_that_states_no_fact_gets_no_report() -> None:
    extracted, _ = candidate(
        FactProposal(
            kind=MaterialFactKind.AMOUNT,
            subject=subject("component", "fund-living"),
            reason="the page gives no figure for the stipend",
        )
    )

    assert extracted.facts.stated == ()
    assert extracted.facts.unspecified[0].state is FactState.UNSPECIFIED

    with pytest.raises(EvidenceCheckRefused, match="states no material fact"):
        check_candidate(extracted, [], checked_at=CHECKED_AT)
