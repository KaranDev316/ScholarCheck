"""Shared fixtures for backend tests."""

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.domain.enums import (
    DegreeLevel,
    DegreeStatus,
    FundingComponentKind,
    FundingRelationship,
    FundingStatus,
)
from app.domain.models import (
    Evidence,
    FundingComponent,
    Grade,
    OfficialLinks,
    Opportunity,
    Profile,
    Programme,
    Round,
)
from app.main import create_app

RETRIEVED_AT = datetime(2026, 10, 20, 9, 0, tzinfo=UTC)


@pytest.fixture
def settings() -> Settings:
    """Deterministic settings so tests never read the real environment."""

    return Settings(
        app_env="test",
        cors_allowed_origins=("http://localhost:5173",),
        database_url=None,
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture
def evidence() -> Evidence:
    return Evidence(
        id="ev-tuition-waiver",
        url="https://example.edu/scholarships/waiver",
        passage="Tuition fees are waived for the duration of the programme.",
        retrieved_at=RETRIEVED_AT,
    )


@pytest.fixture
def tuition_component(evidence: Evidence) -> FundingComponent:
    return FundingComponent(
        id="fund-tuition",
        kind=FundingComponentKind.TUITION,
        status=FundingStatus.SPECIFIED,
        relationship=FundingRelationship.TUITION_REDUCTION,
        description="Full tuition reduction; fees are not paid to the student.",
        amount=0,
        currency="CAD",
        period="per academic year",
        evidence_refs=(evidence.id,),
    )


@pytest.fixture
def profile() -> Profile:
    """Persona P1: Malawian national, resident in India, three-year BCA."""

    return Profile(
        nationality="MW",
        residence_country="IN",
        degree_type="BCA",
        degree_duration_years=3,
        degree_status=DegreeStatus.ONGOING,
        intended_level=DegreeLevel.RESEARCH_MASTER,
        grade=Grade(value="8", scale="10-point CGPA"),
    )


@pytest.fixture
def opportunity(tuition_component: FundingComponent, evidence: Evidence) -> Opportunity:
    return Opportunity(
        id="example-tuition-waiver",
        scheme_name="Example Tuition Waiver Scheme",
        funder="Example University",
        destinations=("CA",),
        summary="A scheme that waives tuition only; living costs are not covered.",
        links=OfficialLinks(
            summary_url="https://example.edu/scholarships/waiver",
            requirements_url="https://example.edu/scholarships/waiver/requirements",
            portal_url="https://example.edu/apply",
        ),
        programmes=(
            Programme(
                id="prog-example-msc",
                name="MSc Example Research",
                degree_level=DegreeLevel.RESEARCH_MASTER,
                institution="Example University",
                country="CA",
                duration_years=2,
            ),
        ),
        rounds=(Round(id="round-2027", label="2027 entry", intake="September 2027"),),
        funding_components=(tuition_component,),
        evidence=(evidence,),
        last_retrieved_at=RETRIEVED_AT,
    )
