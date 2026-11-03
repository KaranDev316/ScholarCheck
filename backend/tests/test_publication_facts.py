"""T06 / CONTEXT rule 5: a material fact states what the source says, or why not.

A decision-critical field is never a bare ``None``. The fact carries its state —
``stated``, ``unspecified`` or ``conflicting`` — plus the field-level evidence the
gate re-checks, so a reader can tell "the page says 40,000" from "no page states a
figure" from "two pages disagree".
"""

import pytest
from pydantic import ValidationError

from app.domain.enums import DegreeLevel, EligibilityRuleKind
from app.domain.models import EligibilityRule, Programme, Round
from app.publication.facts import (
    DeadlineStage,
    FactReading,
    FactState,
    MaterialFact,
    MaterialFactKind,
    MaterialFacts,
    required_fact_keys,
    subject,
)
from tests.publication_helpers import sample_record

PASSAGE = "The scholarship pays $40,000 per year for 36 months."


def reading(
    value: str = "40000",
    *,
    evidence_id: str = "ev-value",
    snapshot_id: str = "snap-value",
    excerpt: str = PASSAGE,
) -> FactReading:
    return FactReading(
        value=value,
        evidence_id=evidence_id,
        snapshot_id=snapshot_id,
        excerpt=excerpt,
    )


def amount_fact(*readings: FactReading, **kwargs) -> MaterialFact:
    return MaterialFact(
        kind=MaterialFactKind.AMOUNT,
        subject=subject("component", "fund-living"),
        state=kwargs.pop("state", FactState.STATED),
        value=kwargs.pop("value", "40000"),
        readings=readings,
        **kwargs,
    )


def unstated(kind: MaterialFactKind, reason: str) -> MaterialFact:
    return MaterialFact(
        kind=kind,
        subject=subject("component", "fund-living"),
        state=FactState.UNSPECIFIED,
        reason=reason,
    )
def test_a_stated_fact_carries_its_value_and_the_span_that_states_it() -> None:
    fact = amount_fact(reading())

    assert fact.key == "component:fund-living.amount"
    assert fact.value == "40000"
    assert fact.evidence_refs == ("ev-value",)
    assert fact.excerpts == (PASSAGE,)


def test_a_stated_fact_without_a_reading_is_refused() -> None:
    """A value with no quotation is the claim the fact table exists to prevent."""

    with pytest.raises(ValidationError, match="must cite at least one reading"):
        amount_fact()


def test_a_stated_fact_whose_readings_disagree_is_refused() -> None:
    with pytest.raises(ValidationError, match="readings that disagree"):
        amount_fact(reading(), reading("41000", evidence_id="ev-other"))


def test_a_stated_fact_cannot_carry_an_unresolved_reason() -> None:
    with pytest.raises(ValidationError, match="cannot carry an unresolved reason"):
        amount_fact(reading(), reason="one page is ambiguous")


def test_a_stated_value_must_be_one_of_its_readings() -> None:
    with pytest.raises(ValidationError, match="must match its readings"):
        amount_fact(reading(value="41000"), value="40000")


def test_a_stated_stage_must_be_a_stage_the_policy_names() -> None:
    with pytest.raises(ValidationError, match="must be one of"):
        MaterialFact(
            kind=MaterialFactKind.STAGE,
            subject=subject("round", "round-2027"),
            state=FactState.STATED,
            value="sometime in autumn",
            readings=(reading("sometime in autumn"),),
        )

    stated = MaterialFact(
        kind=MaterialFactKind.STAGE,
        subject=subject("round", "round-2027"),
        state=FactState.STATED,
        value=DeadlineStage.SCHOLARSHIP.value,
        readings=(reading(DeadlineStage.SCHOLARSHIP.value),),
    )

    assert stated.value == "scholarship"


def test_an_unspecified_fact_must_say_why_it_is_unspecified() -> None:
    with pytest.raises(ValidationError, match="must say why"):
        MaterialFact(
            kind=MaterialFactKind.RATE_YEAR,
            subject=subject("component", "fund-living"),
            state=FactState.UNSPECIFIED,
        )


def test_an_unspecified_fact_cannot_carry_a_value_or_a_reading() -> None:
    with pytest.raises(ValidationError, match="cannot carry a value or a reading"):
        MaterialFact(
            kind=MaterialFactKind.RATE_YEAR,
            subject=subject("component", "fund-living"),
            state=FactState.UNSPECIFIED,
            readings=(reading(),),
            reason="the page gives no rate year",
        )


def test_a_conflicting_fact_keeps_both_readings_and_publishes_no_value() -> None:
    conflicting = MaterialFact(
        kind=MaterialFactKind.AMOUNT,
        subject=subject("component", "fund-living"),
        state=FactState.CONFLICTING,
        readings=(reading(), reading("41000", evidence_id="ev-other")),
        reason="the summary page and the regulations disagree",
    )

    assert conflicting.value is None
    assert conflicting.evidence_refs == ("ev-value", "ev-other")
    assert conflicting.reason is not None


def test_a_conflicting_fact_needs_two_readings_that_differ() -> None:
    with pytest.raises(ValidationError, match="at least two readings"):
        MaterialFact(
            kind=MaterialFactKind.AMOUNT,
            subject=subject("component", "fund-living"),
            state=FactState.CONFLICTING,
            readings=(reading(),),
            reason="the pages disagree",
        )


def test_a_conflicting_fact_cannot_publish_one_of_its_values() -> None:
    with pytest.raises(ValidationError, match="cannot publish a single value"):
        MaterialFact(
            kind=MaterialFactKind.AMOUNT,
            subject=subject("component", "fund-living"),
            state=FactState.CONFLICTING,
            value="40000",
            readings=(reading(), reading("41000", evidence_id="ev-other")),
            reason="the pages disagree",
        )


def test_the_table_refuses_two_facts_for_one_field() -> None:
    with pytest.raises(ValidationError, match="one fact per field"):
        MaterialFacts(facts=(amount_fact(reading()), amount_fact(reading())))


def test_the_table_finds_and_groups_the_facts_it_holds() -> None:
    stated = amount_fact(reading())
    unstated_year = unstated(MaterialFactKind.RATE_YEAR, "the page gives no rate year")
    facts = MaterialFacts(facts=(stated, unstated_year))

    assert facts.find("component:fund-living.amount") is stated
    assert facts.find("component:fund-living.currency") is None
    assert facts.keys == (
        "component:fund-living.amount",
        "component:fund-living.rate_year",
    )
    assert facts.stated == (stated,)
    assert facts.unspecified == (unstated_year,)
    assert facts.conflicting == ()


def test_the_fingerprint_ignores_order_and_follows_content() -> None:
    stated = amount_fact(reading())
    unstated_year = unstated(MaterialFactKind.RATE_YEAR, "the page gives no rate year")

    forwards = MaterialFacts(facts=(stated, unstated_year))
    backwards = MaterialFacts(facts=(unstated_year, stated))
    changed = MaterialFacts(
        facts=(amount_fact(reading("41000"), value="41000"), unstated_year)
    )

    assert forwards.fingerprint == backwards.fingerprint
    assert forwards.fingerprint != changed.fingerprint
    assert len(forwards.fingerprint) == 64


def test_required_fact_keys_names_every_field_the_record_obliges() -> None:
    record = sample_record().model_copy(
        update={
            "programmes": (
                Programme(
                    id="phd-engineering",
                    name="PhD (Engineering)",
                    degree_level=DegreeLevel.DOCTORAL,
                    institution="Example University",
                    country="AU",
                ),
            ),
            "rounds": (Round(id="round-2027", label="2027 entry"),),
            "eligibility_rules": (
                EligibilityRule(
                    id="enrolment",
                    requirement="The applicant must be enrolled full time.",
                    kind=EligibilityRuleKind.ENROLMENT_STATUS,
                ),
            ),
        }
    )

    keys = required_fact_keys(record)

    assert "component:fund-living.amount" in keys
    assert "component:fund-living.currency" in keys
    assert "component:fund-living.funding_relationship" in keys
    assert "component:fund-living.rate_year" in keys
    assert "round:round-2027.intake" in keys
    assert "round:round-2027.deadline" in keys
    assert "round:round-2027.stage" in keys
    assert "rule:enrolment.eligibility_restriction" in keys
    assert not any(key.startswith("programme:") for key in keys)
    assert len(keys) == len(set(keys))
