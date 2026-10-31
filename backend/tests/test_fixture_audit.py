"""S01 F-05: the first-pass review findings stay enforced as holds.

The register in ``content/publication/first-pass-review.json`` is the
machine-readable form of ``FIRST-PASS-REVIEW.md``. The gate reads it itself, so a
fixture with a recorded finding cannot be published while that finding stands:
not by a report that claims support for every entry, and not by publishing a copy
of the record under a new id.
"""

from pathlib import Path

import pytest

from app.domain.models import Opportunity
from app.publication.contracts import CheckResult, DecisionType
from app.publication.gates import evaluate
from app.publication.register import load_register
from app.storage.opportunities import CONTENT_DIR, read_seed
from tests.publication_helpers import build_report, build_snapshots, load_findings

FINDINGS = load_findings()
SEED_FILES = sorted(CONTENT_DIR.glob("*.yaml"))


def _record(opportunity_id: str) -> Opportunity:
    return read_seed(CONTENT_DIR / f"{opportunity_id}.yaml")


def _retained(snapshots):
    return {snapshot.id: snapshot for snapshot in snapshots}


def test_the_register_records_every_fixture_and_can_be_read() -> None:
    """Nothing is launch-ready, and the register is what keeps it that way."""

    register = load_register()

    assert register.problem is None
    assert set(register.entries) == {read_seed(path).id for path in SEED_FILES}


def test_every_recorded_finding_names_a_real_claim() -> None:
    for opportunity_id, findings in FINDINGS["findings"].items():
        record = _record(opportunity_id)
        citations = {entry.id: str(entry.url) for entry in record.evidence}
        for finding in findings:
            assert finding["evidence_id"] in citations
            assert finding["evidence_url"] == citations[finding["evidence_id"]]
            assert finding["result"] in {member.value for member in CheckResult}
            assert finding["result"] != CheckResult.SUPPORTED.value


@pytest.mark.parametrize("path", SEED_FILES, ids=lambda path: path.stem)
def test_a_held_fixture_cannot_be_published_by_its_own_report(path: Path) -> None:
    """A report claiming support for every entry does not clear a finding."""

    record = read_seed(path)
    snapshots = build_snapshots(record)

    decision = evaluate(
        record,
        build_report(record, snapshots),
        _retained(snapshots),
        register=load_register(),
    )

    assert decision.decision is DecisionType.HOLD
    for finding in FINDINGS["findings"][record.id]:
        assert any(finding["reason"] in reason for reason in decision.reasons)


@pytest.mark.parametrize("path", SEED_FILES, ids=lambda path: path.stem)
def test_a_held_fixture_cannot_be_published_under_a_new_id(path: Path) -> None:
    """The hold follows the page, not the identifier someone chose for it."""

    record = read_seed(path).model_copy(update={"id": f"{path.stem}-copy"})
    snapshots = build_snapshots(record)

    decision = evaluate(
        record,
        build_report(record, snapshots),
        _retained(snapshots),
        register=load_register(),
    )

    assert decision.decision is DecisionType.HOLD
    assert any("open review finding" in reason for reason in decision.reasons)


@pytest.mark.parametrize("path", SEED_FILES, ids=lambda path: path.stem)
def test_a_fixture_without_its_page_retained_is_held(path: Path) -> None:
    """A page that was never snapshotted leaves a claim unchecked."""

    record = read_seed(path)
    missing = record.evidence[0].id
    snapshots = build_snapshots(record, omit=(missing,))

    decision = evaluate(
        record,
        build_report(record, snapshots),
        _retained(snapshots),
        register=load_register(),
    )

    assert decision.decision is DecisionType.HOLD
    assert any(missing in reason for reason in decision.reasons)
