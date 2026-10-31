"""S01 F-08: publishing is one atomic, report-backed step.

Set SCHOLARCHECK_TEST_DATABASE_URL to run the database cases. The first case
runs everywhere and proves the gate decides before the database is touched.
"""

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.publication.contracts import CheckResult, DecisionType
from app.publication.gates import PublicationBlocked
from app.publication.register import FindingsRegister
from app.publication.store import SnapshotConflict, publish, read_snapshot, store_snapshot
from app.storage.opportunities import CONTENT_DIR, read_seed
from tests.publication_helpers import (
    build_report,
    build_snapshots,
    load_findings,
    sample_record,
)

APPROVED = ("nserc-crsng.gc.ca",)
RMIT = ("rmit.edu.au",)


class _NoDatabase:
    """A connection that fails the test if the gate reaches for it."""

    def transaction(self):
        raise AssertionError("the gate must decide before the database is touched")

    def execute(self, *args, **kwargs):
        raise AssertionError("the gate must decide before the database is touched")


def _state(conn: psycopg.Connection, opportunity_id: str):
    return conn.execute(
        """
        SELECT assurance, source_checked_at, validation_policy_version,
               freshness, revision
        FROM publication_state WHERE opportunity_id = %s
        """,
        (opportunity_id,),
    ).fetchone()


def _count(conn: psycopg.Connection, table: str) -> int:
    return conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]


def _settings(dsn: str, environment: str) -> Settings:
    return Settings(
        app_env=environment,
        cors_allowed_origins=("http://localhost:5173",),
        database_url=dsn,
    )


def test_a_held_candidate_never_reaches_the_database() -> None:
    candidate = sample_record()
    snapshots = build_snapshots(candidate)
    report = build_report(
        candidate,
        snapshots,
        results={"ev-value": CheckResult.UNSUPPORTED},
        reasons={"ev-value": "the page states a different amount"},
    )

    with pytest.raises(PublicationBlocked) as blocked:
        publish(_NoDatabase(), candidate, report, snapshots, approved_hosts=APPROVED)

    assert blocked.value.decision.decision is DecisionType.HOLD
    assert blocked.value.decision.reasons


def test_publish_records_the_revision_its_report_and_its_snapshots(test_dsn: str) -> None:
    candidate = sample_record()
    snapshots = build_snapshots(candidate)
    report = build_report(candidate, snapshots)

    with psycopg.connect(test_dsn) as conn:
        revision = publish(conn, candidate, report, snapshots, approved_hosts=APPROVED)

        assert revision.revision == 1
        assert revision.content_hash == report.content_hash
        state = _state(conn, candidate.id)
        assert state[0] == "source_checked"
        assert state[1] == report.checked_at
        assert state[2] == report.policy_version
        assert state[3] == "current"
        assert state[4] == 1

        stored = conn.execute(
            """
            SELECT content_hash, policy_version, report
            FROM opportunity_revisions WHERE opportunity_id = %s AND revision = 1
            """,
            (candidate.id,),
        ).fetchone()
        assert stored[0] == report.content_hash
        assert stored[1] == report.policy_version
        assert stored[2]["checks"][0]["result"] == "supported"

        linked = {
            row[0]
            for row in conn.execute(
                """
                SELECT snapshot_id FROM revision_snapshots
                WHERE opportunity_id = %s AND revision = 1
                """,
                (candidate.id,),
            )
        }
        assert linked == set(revision.decision.snapshot_ids)
        assert read_snapshot(conn, snapshots[0].id) == snapshots[0]


def test_a_published_record_is_served_with_its_check_date(test_dsn: str) -> None:
    candidate = sample_record()
    snapshots = build_snapshots(candidate)
    with psycopg.connect(test_dsn) as conn:
        publish(
            conn,
            candidate,
            build_report(candidate, snapshots),
            snapshots,
            approved_hosts=APPROVED,
        )

    with TestClient(create_app(_settings(test_dsn, "production"))) as client:
        response = client.get(f"/api/v1/opportunities/{candidate.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["isPublished"] is True
    assert body["publication"]["assurance"] == "source_checked"
    assert body["publication"]["sourceCheckedAt"] is not None
    assert (
        body["publication"]["validationPolicyVersion"]
        == build_report(candidate, snapshots).policy_version
    )


def test_publishing_the_same_facts_twice_keeps_one_revision(test_dsn: str) -> None:
    candidate = sample_record()
    snapshots = build_snapshots(candidate)
    report = build_report(candidate, snapshots)

    with psycopg.connect(test_dsn) as conn:
        first = publish(conn, candidate, report, snapshots, approved_hosts=APPROVED)
        second = publish(conn, candidate, report, snapshots, approved_hosts=APPROVED)

        assert first.revision == second.revision == 1
        assert _count(conn, "opportunity_revisions") == 1


def test_an_unsupported_fixture_leaves_no_trace(test_dsn: str) -> None:
    """The real RMIT candidate is held and nothing about it becomes public."""

    candidate = read_seed(CONTENT_DIR / "rmit-research-stipend.yaml")
    snapshots = build_snapshots(candidate)
    report = build_report(candidate, snapshots)

    with psycopg.connect(test_dsn) as conn:
        with pytest.raises(PublicationBlocked):
            publish(conn, candidate, report, snapshots, approved_hosts=RMIT)

        assert _count(conn, "source_snapshots") == 0
        assert _count(conn, "opportunity_revisions") == 0
        assert _count(conn, "opportunities") == 0

    with TestClient(create_app(_settings(test_dsn, "production"))) as client:
        hidden = client.get(f"/api/v1/opportunities/{candidate.id}")

    assert hidden.status_code == 404
    assert hidden.json()["code"] == "opportunity_not_found"


def test_publishing_cannot_omit_the_recorded_findings() -> None:
    """A perfect report and no argument to drop them: RMIT still holds."""

    candidate = read_seed(CONTENT_DIR / "rmit-research-stipend.yaml")
    snapshots = build_snapshots(candidate)
    report = build_report(candidate, snapshots)
    expected = [
        item["reason"] for item in load_findings()["findings"][candidate.id]
    ]

    with pytest.raises(PublicationBlocked) as blocked:
        publish(_NoDatabase(), candidate, report, snapshots, approved_hosts=RMIT)

    decision = blocked.value.decision
    assert decision.decision is DecisionType.HOLD
    for reason in expected:
        assert any(reason in held for held in decision.reasons), reason


def test_a_held_fixture_cannot_be_published_under_a_new_id() -> None:
    """Renaming the record does not move the page out from under the finding."""

    original = read_seed(CONTENT_DIR / "rmit-research-stipend.yaml")
    candidate = original.model_copy(update={"id": "rmit-research-stipend-copy"})
    snapshots = build_snapshots(candidate)
    report = build_report(candidate, snapshots)

    with pytest.raises(PublicationBlocked) as blocked:
        publish(_NoDatabase(), candidate, report, snapshots, approved_hosts=RMIT)

    assert blocked.value.decision.decision is DecisionType.HOLD
    assert any(
        "open review finding" in reason for reason in blocked.value.decision.reasons
    )


def test_an_unreadable_register_holds_every_candidate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deleting or breaking the register must not read as "nothing outstanding"."""

    monkeypatch.setattr(
        "app.publication.store.load_register",
        lambda: FindingsRegister(problem="first-pass-review.json: no such file"),
    )
    candidate = sample_record()
    snapshots = build_snapshots(candidate)
    report = build_report(candidate, snapshots)

    with pytest.raises(PublicationBlocked) as blocked:
        publish(_NoDatabase(), candidate, report, snapshots, approved_hosts=APPROVED)

    assert blocked.value.decision.decision is DecisionType.HOLD
    assert any(
        "could not be read" in reason for reason in blocked.value.decision.reasons
    )


def test_a_failure_half_way_through_rolls_every_write_back(
    test_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = sample_record()
    snapshots = build_snapshots(candidate)
    report = build_report(candidate, snapshots)

    def fail(conn: psycopg.Connection, opportunity: object) -> None:
        raise RuntimeError("write failed half way")

    monkeypatch.setattr("app.publication.store.write_payload", fail)

    with psycopg.connect(test_dsn) as conn:
        with pytest.raises(RuntimeError):
            publish(conn, candidate, report, snapshots, approved_hosts=APPROVED)

        assert _count(conn, "source_snapshots") == 0
        assert _count(conn, "opportunity_revisions") == 0
        assert _count(conn, "opportunities") == 0


def test_a_retained_snapshot_cannot_be_rewritten(test_dsn: str) -> None:
    snapshot = build_snapshots(sample_record())[0]

    with psycopg.connect(test_dsn) as conn:
        assert store_snapshot(conn, snapshot) is True
        assert store_snapshot(conn, snapshot) is False
        with pytest.raises(SnapshotConflict):
            store_snapshot(conn, snapshot.model_copy(update={"body": "a different page"}))
        assert read_snapshot(conn, snapshot.id) == snapshot

    with psycopg.connect(test_dsn) as conn:
        with pytest.raises(psycopg.errors.RaiseException, match="immutable"):
            conn.execute(
                "UPDATE source_snapshots SET body = 'rewritten' WHERE id = %s",
                (snapshot.id,),
            )


def test_the_database_refuses_a_source_check_without_a_revision(test_dsn: str) -> None:
    candidate = sample_record()
    snapshots = build_snapshots(candidate)

    with psycopg.connect(test_dsn) as conn:
        publish(
            conn,
            candidate,
            build_report(candidate, snapshots),
            snapshots,
            approved_hosts=APPROVED,
        )
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            conn.execute(
                "DELETE FROM opportunity_revisions WHERE opportunity_id = %s",
                (candidate.id,),
            )
        conn.rollback()


def test_human_verified_is_not_a_storable_assurance(test_dsn: str) -> None:
    candidate = sample_record()
    snapshots = build_snapshots(candidate)
    with psycopg.connect(test_dsn) as conn:
        publish(
            conn,
            candidate,
            build_report(candidate, snapshots),
            snapshots,
            approved_hosts=APPROVED,
        )

    with psycopg.connect(test_dsn) as conn:
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute(
                "UPDATE publication_state SET assurance = 'human_verified' "
                "WHERE opportunity_id = %s",
                (candidate.id,),
            )

    with psycopg.connect(test_dsn) as conn:
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute(
                """
                UPDATE publication_state
                SET assurance = 'source_checked', source_checked_at = now(),
                    validation_policy_version = 's01.publication.1', revision = NULL
                WHERE opportunity_id = %s
                """,
                (candidate.id,),
            )
