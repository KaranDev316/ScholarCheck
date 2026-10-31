"""S01 F-05: the first-pass review findings stay enforced as holds.

The register in ``content/publication/first-pass-review.json`` is the
machine-readable form of ``FIRST-PASS-REVIEW.md``. A fixture with a recorded
finding cannot be published while that finding stands, and a fixture whose
page was never retained cannot be published either.
"""

from pathlib import Path

import pytest

from app.domain.models import Opportunity
from app.publication.contracts import CheckResult, DecisionType
from app.publication.gates import evaluate
from app.storage.opportunities import CONTENT_DIR, read_seed
from tests.publication_helpers import build_report, build_snapshots, load_findings

FINDINGS = load_findings()
SEED_FILES = sorted(CONTENT_DIR.glob("*.yaml"))


def _record(opportunity_id: str) -> Opportunity:
    path = CONTENT_DIR / f"{opportunity_id}.yaml"
    return read_seed(path)


def _retained(snapshots):
    return {snapshot.id: snapshot for snapshot in snapshots}


def test_every_recorded_finding_names_a_real_claim() -> None:
    for opportunity_id, findings in FINDINGS["findings"].items():
        record = _record(opportunity_id)
        evidence_ids = {entry.id for entry in record.evidence}
        for finding in findings:
            assert finding["evidence_id"] in evidence_ids
            assert finding["result"] in {member.value for member in CheckResult}


@pytest.mark.parametrize("path", SEED_FILES, ids=lambda path: path.stem)
def test_each_fixture_still_carries_an_open_finding(path: Path) -> None:
    """None of the four fixtures is launch-ready; fixing one updates the register."""

    record = read_seed(path)

    assert FINDINGS["findings"].get(record.id), f"{record.id} has no open finding"


@pytest.mark.parametrize("path", SEED_FILES, ids=lambda path: path.stem)
def test_a_fixture_with_an_unresolved_finding_is_held(path: Path) -> None:
    record = read_seed(path)
    findings = FINDINGS["findings"][record.id]
    snapshots = build_snapshots(record)
    report = build_report(
        record,
        snapshots,
        results={item["evidence_id"]: CheckResult(item["result"]) for item in findings},
        reasons={item["evidence_id"]: item["reason"] for item in findings},
    )

    decision = evaluate(record, report, _retained(snapshots))

    assert decision.decision is DecisionType.HOLD
    for finding in findings:
        assert any(finding["evidence_id"] in reason for reason in decision.reasons)


@pytest.mark.parametrize("path", SEED_FILES, ids=lambda path: path.stem)
def test_an_open_finding_holds_even_a_fully_supporting_report(path: Path) -> None:
    """A maxed-out report cannot publish a record with an unresolved finding."""

    record = read_seed(path)
    findings = FINDINGS["findings"][record.id]
    snapshots = build_snapshots(record)
    report = build_report(record, snapshots)

    decision = evaluate(
        record,
        report,
        _retained(snapshots),
        open_findings=tuple(item["reason"] for item in findings),
    )

    assert decision.decision is DecisionType.HOLD
    assert all(
        any(item["reason"] in reason for reason in decision.reasons)
        for item in findings
    )


@pytest.mark.parametrize("path", SEED_FILES, ids=lambda path: path.stem)
def test_a_fixture_without_its_page_retained_is_held(path: Path) -> None:
    """A page that was never snapshotted leaves a claim unchecked."""

    record = read_seed(path)
    missing = record.evidence[0].id
    snapshots = build_snapshots(record, omit=(missing,))

    decision = evaluate(record, build_report(record, snapshots), _retained(snapshots))

    assert decision.decision is DecisionType.HOLD
    assert any(missing in reason for reason in decision.reasons)
