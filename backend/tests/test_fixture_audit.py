"""S01 F-05: recorded review findings stay enforced, and the evidence is real.

The register in ``content/publication/first-pass-review.json`` is the
machine-readable form of ``FIRST-PASS-REVIEW.md``. The gate reads it itself, so a
fixture with a recorded finding cannot be published while that finding stands:
not by a report that claims support for every entry, and not by publishing a copy
of the record under a new id.

The second half of this file checks the other direction: every passage a fixture
quotes must occur in the snapshot retained for that page. A citation that names a
page we never retained, or text the page does not contain, is not evidence.
"""

from datetime import datetime
from pathlib import Path

import pytest

from app.collect.extract import extract_text
from app.domain.hashing import content_hash
from app.domain.models import Opportunity
from app.publication.contracts import (
    CheckResult,
    ClaimCheck,
    DecisionType,
    SourceSnapshot,
    ValidationReport,
)
from app.publication.gates import evaluate
from app.publication.policy import POLICY_VERSION
from app.publication.register import load_register
from app.storage.opportunities import CONTENT_DIR, read_seed
from tests.publication_helpers import (
    build_facts,
    build_report,
    build_snapshots,
    fact_checks,
    load_findings,
    no_findings,
)

FINDINGS = load_findings()
SEED_FILES = sorted(CONTENT_DIR.glob("*.yaml"))
SNAPSHOT_DIR = CONTENT_DIR.parent / "snapshots"
FINDING_CASES = [
    (opportunity_id, finding)
    for opportunity_id, findings in FINDINGS["findings"].items()
    for finding in findings
]
HELD_IDS = sorted(FINDINGS["findings"])


def _record(opportunity_id: str) -> Opportunity:
    return read_seed(CONTENT_DIR / f"{opportunity_id}.yaml")


def _retained(snapshots):
    return {snapshot.id: snapshot for snapshot in snapshots}


def _artifacts() -> dict[str, dict]:
    import json

    return {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(SNAPSHOT_DIR.glob("*.json"))
    }


def _snapshots_by_url() -> dict[str, dict]:
    return {data["snapshot"]["url"]: data["snapshot"] for data in _artifacts().values()}


def test_the_register_is_readable_and_names_only_real_fixtures() -> None:
    """A register entry that names no fixture would hold nothing at all."""

    register = load_register()

    assert register.problem is None
    assert set(register.entries) <= {read_seed(path).id for path in SEED_FILES}


def test_the_unresolved_round_is_recorded_as_a_hold() -> None:
    """RMIT's 2027 round cannot be dated or priced, so it stays held."""

    assert HELD_IDS == ["rmit-research-stipend"]
    assert load_register().holds(read_seed(CONTENT_DIR / "rmit-research-stipend.yaml"))


@pytest.mark.parametrize("path", SEED_FILES, ids=lambda path: path.stem)
def test_every_cited_page_was_retained(path: Path) -> None:
    """A passage can only be checked if the page it came from is still here."""

    record = read_seed(path)
    retained = _snapshots_by_url()

    for entry in record.evidence:
        assert str(entry.url) in retained, f"{entry.id} cites a page that was never retained"


@pytest.mark.parametrize("path", SEED_FILES, ids=lambda path: path.stem)
def test_every_passage_occurs_in_its_retained_snapshot(path: Path) -> None:
    """No paraphrased or transcribed passage can pass as a quotation."""

    record = read_seed(path)
    retained = _snapshots_by_url()

    for entry in record.evidence:
        body = retained[str(entry.url)]["body"]
        quoted = " ".join(entry.passage.split())
        assert quoted in " ".join(body.split()), (
            f"{entry.id} quotes text that is not in the retained snapshot"
        )


@pytest.mark.parametrize("path", SEED_FILES, ids=lambda path: path.stem)
def test_the_fixture_records_the_retrieval_it_was_checked_against(path: Path) -> None:
    """The gate compares timestamps, so a stale one is a silent hold."""

    record = read_seed(path)
    retained = _snapshots_by_url()

    for entry in record.evidence:
        stamped = datetime.fromisoformat(
            retained[str(entry.url)]["retrievedAt"].replace("Z", "+00:00")
        )
        assert entry.retrieved_at == stamped, f"{entry.id} records a different retrieval"


def test_retained_snapshots_keep_their_provenance() -> None:
    """Every artifact says where it came from and whether fetching was allowed."""

    for name, data in _artifacts().items():
        snapshot = data["snapshot"]
        provenance = data["provenance"]

        assert name == f"{snapshot['id']}.json"
        assert snapshot["body"].strip(), f"{name} retained no text"
        assert provenance["robotsAllowed"] is True
        assert provenance["httpStatus"] == snapshot["responseStatus"] == 200
        assert len(provenance["rawSha256"]) == 64
        assert provenance["parserVersion"] == snapshot["parserVersion"]
        assert snapshot["body"] == extract_text(snapshot["body"]), (
            f"{name} is not stable under the current parser; re-collect it"
        )


def test_every_recorded_finding_names_a_real_claim() -> None:
    for opportunity_id, findings in FINDINGS["findings"].items():
        record = _record(opportunity_id)
        citations = {entry.id: str(entry.url) for entry in record.evidence}
        for finding in findings:
            assert finding["evidence_id"] in citations
            assert finding["evidence_url"] == citations[finding["evidence_id"]]
            assert finding["result"] in {member.value for member in CheckResult}
            assert finding["result"] != CheckResult.SUPPORTED.value


@pytest.mark.parametrize(
    ("opportunity_id", "finding"),
    FINDING_CASES,
    ids=lambda value: value.get("evidence_id", value) if isinstance(value, dict) else value,
)
def test_each_known_finding_fails_the_publication_gate(
    opportunity_id: str, finding: dict[str, str]
) -> None:
    """Each first-pass issue independently holds its fixture when checking fails."""

    record = _record(opportunity_id)
    snapshots = build_snapshots(record)
    report = build_report(
        record,
        snapshots,
        results={finding["evidence_id"]: CheckResult(finding["result"])},
        reasons={finding["evidence_id"]: finding["reason"]},
    )

    decision = evaluate(
        record,
        report,
        _retained(snapshots),
        register=no_findings(),
    )

    assert decision.decision is DecisionType.HOLD
    assert any(
        finding["evidence_id"] in reason and finding["reason"] in reason
        for reason in decision.reasons
    )


@pytest.mark.parametrize("opportunity_id", HELD_IDS)
def test_a_held_fixture_cannot_be_published_by_its_own_report(opportunity_id: str) -> None:
    """A report claiming support for every entry does not clear a finding."""

    record = read_seed(CONTENT_DIR / f"{opportunity_id}.yaml")
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


@pytest.mark.parametrize("opportunity_id", HELD_IDS)
def test_a_held_fixture_cannot_be_published_under_a_new_id(opportunity_id: str) -> None:
    """The hold follows the page, not the identifier someone chose for it."""

    held = read_seed(CONTENT_DIR / f"{opportunity_id}.yaml")
    record = held.model_copy(update={"id": f"{opportunity_id}-copy"})
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


LAUNCH_CANDIDATES = ("cgsd-doctoral", "udem-exemption-doctoral", "usyd-rtp-stipend")


def _retained_snapshots_by_id() -> dict[str, SourceSnapshot]:
    return {
        data["snapshot"]["id"]: SourceSnapshot.model_validate(data["snapshot"])
        for data in _artifacts().values()
    }


def _retained_snapshots_by_url() -> dict[str, SourceSnapshot]:
    return {
        data["snapshot"]["url"]: SourceSnapshot.model_validate(data["snapshot"])
        for data in _artifacts().values()
    }


def _supported_report(record: Opportunity) -> ValidationReport:
    """A report claiming support for every entry and every stated fact.

    The snapshots are the ones retained under ``content/snapshots``, so the
    deterministic checks run against real pages. The verdicts are synthetic: this
    proves the gate, not that the claims are true.
    """

    retained = _retained_snapshots_by_url()
    snapshots = tuple(retained.values())
    facts = build_facts(record, snapshots=snapshots)
    checks = [
        ClaimCheck(
            claim=f"{entry.id} passage",
            evidence_id=entry.id,
            snapshot_id=retained[str(entry.url)].id,
            excerpt=entry.passage,
            result=CheckResult.SUPPORTED,
        )
        for entry in record.evidence
    ]
    checks.extend(fact_checks(record, facts))
    return ValidationReport(
        opportunity_id=record.id,
        content_hash=content_hash(record),
        policy_version=POLICY_VERSION,
        checked_at=max(entry.retrieved_at for entry in record.evidence),
        facts=facts,
        checks=tuple(checks),
    )


@pytest.mark.parametrize("opportunity_id", LAUNCH_CANDIDATES)
def test_a_launch_candidate_clears_every_structural_gate(opportunity_id: str) -> None:
    """Hosts, retrieval times, passages and amounts all hold against real pages.

    The report is synthetic, so this proves the deterministic checks only: it
    does not show the claims are true, which is the evidence-check pass's job,
    and it publishes nothing.
    """

    record = read_seed(CONTENT_DIR / f"{opportunity_id}.yaml")

    decision = evaluate(
        record,
        _supported_report(record),
        _retained_snapshots_by_id(),
        register=load_register(),
    )

    assert decision.decision is DecisionType.PUBLISH
    assert decision.reasons == ()
    assert decision.snapshot_ids


def test_the_held_candidate_fails_only_on_its_recorded_finding() -> None:
    """The held record's other checks pass; the finding is what stops it."""

    record = read_seed(CONTENT_DIR / "rmit-research-stipend.yaml")

    decision = evaluate(
        record,
        _supported_report(record),
        _retained_snapshots_by_id(),
        register=load_register(),
    )

    assert decision.decision is DecisionType.HOLD
    assert len(decision.reasons) == len(FINDINGS["findings"][record.id])
    assert all("open review finding" in reason for reason in decision.reasons)
