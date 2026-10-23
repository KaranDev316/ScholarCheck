"""T03: the seed format is structured, evidenced and honestly unverified."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from app.domain.enums import FundingComponentKind, FundingStatus, FundingRelationship
from app.domain.models import FundingComponent, Opportunity, Round

CONTENT_DIR = Path(__file__).resolve().parents[2] / "content" / "opportunities"
SEED_FILES = sorted(CONTENT_DIR.glob("*.yaml"))

EXPECTED_IDS = {
    "cgsd-doctoral",
    "rmit-research-stipend",
    "udem-exemption-doctoral",
    "usyd-rtp-stipend",
}


@pytest.fixture(params=SEED_FILES, ids=lambda path: path.stem)
def seed_path(request: pytest.FixtureRequest) -> Path:
    return request.param


def _raw(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load(path: Path) -> Opportunity:
    return Opportunity.model_validate(_raw(path))


def _all_ids(opportunity: Opportunity) -> list[str]:
    return [
        *(programme.id for programme in opportunity.programmes),
        *(round_.id for round_ in opportunity.rounds),
        *(rule.id for rule in opportunity.eligibility_rules),
        *(component.id for component in opportunity.funding_components),
        *(entry.id for entry in opportunity.evidence),
    ]


def _refs(opportunity: Opportunity) -> list[str]:
    return [
        *(ref for rule in opportunity.eligibility_rules for ref in rule.evidence_refs),
        *(
            ref
            for component in opportunity.funding_components
            for ref in component.evidence_refs
        ),
    ]


def test_t03_fixture_set_matches_the_planned_register() -> None:
    """Four regression fixtures cover the four original demo shapes."""

    assert {path.stem for path in SEED_FILES} == EXPECTED_IDS


def test_t03_seed_files_load_as_domain_opportunities(seed_path: Path) -> None:
    opportunity = _load(seed_path)

    assert opportunity.id == seed_path.stem
    assert opportunity.scheme_name
    assert opportunity.summary
    assert opportunity.programmes, "a fixture without a programme cannot be assessed"
    assert opportunity.eligibility_rules, "a fixture without rules hides its blockers"
    assert opportunity.funding_components
    assert opportunity.evidence


def test_t03_ids_are_unique_and_every_reference_resolves(seed_path: Path) -> None:
    opportunity = _load(seed_path)
    ids = _all_ids(opportunity)

    assert sorted(ids) == sorted(set(ids)), "ids must be unique within a record"
    known = {entry.id for entry in opportunity.evidence}

    for ref in _refs(opportunity):
        assert ref in known, f"{ref} does not resolve to evidence in {opportunity.id}"


def test_t03_only_date_evidence_may_stand_unreferenced(seed_path: Path) -> None:
    """Round labels cite published dates, but ``Round`` has no ref field in S01."""

    opportunity = _load(seed_path)
    referenced = set(_refs(opportunity))

    for entry in opportunity.evidence:
        if entry.id not in referenced:
            assert "deadline" in entry.passage.lower(), (
                f"{entry.id} backs no rule or component"
            )


def test_t03_blocking_rules_are_evidenced(seed_path: Path) -> None:
    opportunity = _load(seed_path)

    assert any(rule.blocking for rule in opportunity.eligibility_rules)

    for rule in opportunity.eligibility_rules:
        if rule.blocking:
            assert rule.evidence_refs, f"{rule.id} blocks without evidence"


def test_t03_components_with_a_value_are_evidenced(seed_path: Path) -> None:
    opportunity = _load(seed_path)

    for component in opportunity.funding_components:
        if component.status is FundingStatus.UNSPECIFIED:
            assert component.amount is None
            assert component.currency is None
            continue

        assert component.evidence_refs, f"{component.id} states a value unprompted"
        assert component.amount is not None or component.period is not None


def test_t03_retrieval_and_verification_stay_separate(seed_path: Path) -> None:
    """Agent checks must not claim optional human verification."""

    opportunity = _load(seed_path)
    assert opportunity.last_verified_at is None
    assert all(entry.verified_at is None for entry in opportunity.evidence)
    assert all(entry.verified_by is None for entry in opportunity.evidence)


def test_t03_last_retrieved_at_matches_the_evidence(seed_path: Path) -> None:
    opportunity = _load(seed_path)
    latest = max(entry.retrieved_at for entry in opportunity.evidence)

    assert opportunity.last_retrieved_at == latest
    assert latest.tzinfo is not None
    assert latest <= datetime.now(UTC)


def test_t03_funding_is_never_summed(seed_path: Path) -> None:
    """CONTEXT rule 3: components are shown one by one, with no total."""

    fields = set(FundingComponent.model_fields)
    raw: dict[str, Any] = _raw(seed_path)

    assert {"total", "sum", "combined"} & fields == set()
    for entry in raw["funding_components"]:
        assert {"total", "sum", "combined"} & set(entry) == set()


def test_t03_exemption_fixture_is_a_tuition_reduction() -> None:
    """AC-10: an exemption is labelled as a tuition reduction, not a stipend."""

    opportunity = _load(CONTENT_DIR / "udem-exemption-doctoral.yaml")
    tuition = [
        component
        for component in opportunity.funding_components
        if component.kind is FundingComponentKind.TUITION
    ]
    living = [
        component
        for component in opportunity.funding_components
        if component.kind is FundingComponentKind.LIVING_SUPPORT
    ]

    assert len(tuition) == 1
    assert tuition[0].relationship is FundingRelationship.TUITION_REDUCTION
    assert tuition[0].amount is not None
    assert tuition[0].currency == "CAD"
    assert tuition[0].period
    assert living and living[0].status is FundingStatus.UNSPECIFIED


def test_t03_multi_stage_fixture_names_its_stages() -> None:
    opportunity = _load(CONTENT_DIR / "rmit-research-stipend.yaml")

    assert opportunity.rounds
    assert "expression of interest" in (opportunity.rounds[0].route or "")
    assert any(
        "expression of interest" in entry.passage for entry in opportunity.evidence
    )


def test_t03_rounds_carry_identity_only() -> None:
    """S02 owns deadline status; S01 rounds must not smuggle in a computed date."""

    assert set(Round.model_fields) == {"id", "label", "intake", "route"}
