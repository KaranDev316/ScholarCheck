"""Shared fixtures for backend tests."""

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg import sql
from psycopg.conninfo import make_conninfo

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
from app.storage.opportunities import create_schema

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
def test_dsn() -> Iterator[str]:
    """A disposable PostgreSQL schema, or skip when no server is configured."""

    base_dsn = os.getenv("SCHOLARCHECK_TEST_DATABASE_URL")
    if not base_dsn:
        pytest.skip("SCHOLARCHECK_TEST_DATABASE_URL is not set")

    schema = f"scholarcheck_test_{uuid4().hex}"
    with psycopg.connect(base_dsn, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        try:
            scoped_dsn = make_conninfo(base_dsn, options=f"-csearch_path={schema}")
            with psycopg.connect(scoped_dsn) as conn:
                create_schema(conn)
            yield scoped_dsn
        finally:
            admin.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
            )


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
