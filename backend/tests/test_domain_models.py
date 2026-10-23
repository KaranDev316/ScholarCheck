"""T02: domain types enforce the rules the product depends on."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.domain.enums import (
    AssessmentOutcome,
    DegreeLevel,
    EligibilityRuleKind,
    FundingStatus,
)
from app.domain.models import (
    AssessmentResult,
    EligibilityRule,
    Evidence,
    FundingComponent,
    Grade,
    Profile,
    RuleAssessment,
)

RETRIEVED_AT = datetime(2026, 10, 20, 9, 0, tzinfo=UTC)


def test_t02_outcome_vocabulary_is_exactly_four_values() -> None:
    """AC-08 / invariant 3: four outcomes, no score or probability wording."""

    values = [member.value for member in AssessmentOutcome]

    assert values == [
        "meets_checked_requirements",
        "potential_fit_confirmation_needed",
        "does_not_meet_stated_requirement",
        "insufficient_information",
    ]
    assert all("%" not in value and "score" not in value for value in values)


def test_t02_unknown_outcome_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AssessmentResult(
            opportunity_id="example-scheme",
            outcome="80_percent_match",
            outcome_reason="Looks promising.",
            rules=(),
        )


def test_t02_degree_levels_cover_bachelors_masters_and_doctoral() -> None:
    """D-08: every level the product serves is representable, and distinct."""

    assert [level.value for level in DegreeLevel] == [
        "bachelor",
        "taught_master",
        "research_master",
        "doctoral",
    ]


@pytest.mark.parametrize("level", list(DegreeLevel))
def test_t02_profile_accepts_each_degree_level(
    level: DegreeLevel, profile: Profile
) -> None:
    variant = profile.model_copy(update={"intended_level": level})

    assert variant.intended_level is level
    assert variant.model_dump(mode="json", by_alias=True)["intendedLevel"] == (
        level.value
    )


def test_t02_unknown_degree_level_is_rejected(profile: Profile) -> None:
    """Levels are a closed vocabulary; a made-up one must not slip through."""

    payload = profile.model_dump()
    payload["intended_level"] = "postdoc"

    with pytest.raises(ValidationError):
        Profile(**payload)


def test_t02_grade_is_kept_verbatim(profile: Profile) -> None:
    """AC-03 / invariant 6: no parsing, no conversion to another scale."""

    assert profile.grade is not None
    assert profile.grade.value == "8"
    assert profile.grade.scale == "10-point CGPA"
    assert profile.model_dump(mode="json")["grade"] == {
        "value": "8",
        "scale": "10-point CGPA",
    }


def test_t02_grade_stays_a_string() -> None:
    """A numeric grade would tempt a conversion; the value stays text."""

    grade = Grade.model_validate({"value": "3.5", "scale": "4.0 CGPA"})

    assert grade.value == "3.5"


def test_t02_evidence_keeps_retrieved_and_verified_separate(
    evidence: Evidence,
) -> None:
    """Invariant 5: an automatic fetch never counts as human verification."""

    assert evidence.retrieved_at == RETRIEVED_AT
    assert evidence.verified_at is None
    assert evidence.verified_by is None

    refreshed = evidence.model_copy(
        update={"retrieved_at": RETRIEVED_AT + timedelta(days=7)}
    )

    assert refreshed.retrieved_at > evidence.retrieved_at
    assert refreshed.verified_at is None


def test_t02_evidence_requires_timezone_aware_timestamps() -> None:
    with pytest.raises(ValidationError):
        Evidence(
            id="ev-naive",
            url="https://example.edu/page",
            passage="Some text.",
            retrieved_at=datetime(2026, 10, 20, 9, 0),
        )


def test_t02_verification_cannot_precede_retrieval() -> None:
    with pytest.raises(ValidationError):
        Evidence(
            id="ev-backwards",
            url="https://example.edu/page",
            passage="Some text.",
            retrieved_at=datetime(2026, 10, 20, 9, 0, tzinfo=UTC),
            verified_at=datetime(2026, 10, 19, 9, 0, tzinfo=UTC),
            verified_by="reviewer",
        )


def test_t02_rule_without_evidence_is_allowed_but_has_no_reference() -> None:
    """AC-11: an unevidenced rule exists and is therefore unverified."""

    rule = EligibilityRule(
        id="rule-degree-recognition",
        requirement="The degree must be recognised as equivalent to a Canadian bachelor's.",
        kind=EligibilityRuleKind.INSTITUTION_RECOGNITION,
        blocking=True,
    )

    assert rule.evidence_refs == ()
    assert rule.blocking is True


def test_t02_rule_assessment_carries_a_reason() -> None:
    """Every result must explain itself in the student's language."""

    with pytest.raises(ValidationError):
        RuleAssessment(rule_id="rule-degree", result="unresolved", reason="")
