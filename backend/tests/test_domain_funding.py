"""T02: funding, profile and wire-format invariants."""

import pytest
from pydantic import ValidationError

from app.domain.enums import FundingStatus
from app.domain.models import FundingComponent, Profile


def test_t02_unspecified_funding_cannot_carry_an_amount() -> None:
    """Invariant 2: missing funding is never shown as zero or as full."""

    with pytest.raises(ValidationError):
        FundingComponent(
            id="fund-living",
            kind="living_support",
            status=FundingStatus.UNSPECIFIED,
            amount=0,
        )


def test_t02_currency_without_amount_is_rejected() -> None:
    with pytest.raises(ValidationError):
        FundingComponent(
            id="fund-travel",
            kind="travel",
            status=FundingStatus.PARTIAL,
            currency="CAD",
        )


def test_t02_unspecified_component_serialises_without_a_value() -> None:
    component = FundingComponent(
        id="fund-living",
        kind="living_support",
        status=FundingStatus.UNSPECIFIED,
    )

    payload = component.model_dump(mode="json", by_alias=True)

    assert payload["status"] == "unspecified"
    assert payload["amount"] is None
    assert payload["currency"] is None
    assert "total" not in payload


def test_t02_domain_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        FundingComponent(
            id="fund-tuition",
            kind="tuition",
            status=FundingStatus.SPECIFIED,
            total_awarded=5000,
        )


def test_t02_domain_models_are_frozen(profile: Profile) -> None:
    with pytest.raises(ValidationError):
        profile.degree_type = "BSc"


def test_t02_country_codes_are_validated() -> None:
    with pytest.raises(ValidationError):
        Profile(
            nationality="Malawi",
            residence_country="IN",
            degree_type="BCA",
            degree_duration_years=3,
            degree_status="ongoing",
            intended_level="research_master",
        )


def test_t02_degree_duration_must_be_plausible() -> None:
    with pytest.raises(ValidationError):
        Profile(
            nationality="MW",
            residence_country="IN",
            degree_type="BCA",
            degree_duration_years=0,
            degree_status="ongoing",
            intended_level="research_master",
        )


def test_t02_wire_format_is_camel_case(profile: Profile) -> None:
    """TypeScript keeps camelCase; Python keeps snake_case."""

    payload = profile.model_dump(mode="json", by_alias=True)

    assert payload["residenceCountry"] == "IN"
    assert payload["degreeDurationYears"] == 3
    assert payload["grade"] == {"value": "8", "scale": "10-point CGPA"}
