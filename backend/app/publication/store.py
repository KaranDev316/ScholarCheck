"""Atomic, evidenced publication.

``publish`` is the only way a record becomes public. It runs the code gate
first, and only then writes, inside one transaction: retained snapshots, the
new facts, an immutable revision with its validation report and snapshot
references, and the ``source_checked`` state pointing at that revision. If any
step fails, nothing from the attempt survives — a candidate cannot end up
half-published or marked checked without a report behind it.

Re-processing the same snapshot produces the same content hash, so an unchanged
record does not gain a duplicate revision.

The review findings register is read here, from ``content/publication``, and is
not a parameter: a caller cannot publish a held candidate by leaving the
findings out, and an unreadable register holds every candidate.
"""

from collections.abc import Sequence

import psycopg
from psycopg.types.json import Jsonb

from app.domain.hashing import content_hash
from app.domain.models import Opportunity
from app.publication.contracts import (
    DecisionType,
    PublicationDecision,
    PublishedRevision,
    SourceSnapshot,
    ValidationReport,
)
from app.publication.gates import PublicationBlocked, evaluate
from app.publication.policy import APPROVED_SOURCE_HOSTS, POLICY_VERSION
from app.publication.register import load_register
from app.storage.opportunities import write_payload


class SnapshotConflict(Exception):
    """Raised when a stored snapshot id is reused for different content."""


def store_snapshot(conn: psycopg.Connection, snapshot: SourceSnapshot) -> bool:
    """Retain a snapshot once; return False when the same content is stored."""

    with conn.transaction():
        return _store_snapshot(conn, snapshot)


def _store_snapshot(conn: psycopg.Connection, snapshot: SourceSnapshot) -> bool:
    row = conn.execute(
        "SELECT content_hash, url, retrieved_at, parser_version, response_status FROM source_snapshots WHERE id = %s", (snapshot.id,)
    ).fetchone()
    if row is not None:
        if tuple(row) != (snapshot.content_hash, str(snapshot.url), snapshot.retrieved_at, snapshot.parser_version, snapshot.response_status):
            raise SnapshotConflict(
                f"snapshot {snapshot.id} is already retained with different content"
            )
        return False

    conn.execute(
        """
        INSERT INTO source_snapshots
            (id, url, body, content_hash, response_status, retrieved_at, parser_version)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            snapshot.id,
            str(snapshot.url),
            snapshot.body,
            snapshot.content_hash,
            snapshot.response_status,
            snapshot.retrieved_at,
            snapshot.parser_version,
        ),
    )
    return True


def read_snapshot(conn: psycopg.Connection, snapshot_id: str) -> SourceSnapshot | None:
    """Read a retained snapshot back, or None when it was never stored."""

    row = conn.execute(
        """
        SELECT id, url, body, response_status, retrieved_at, parser_version
        FROM source_snapshots WHERE id = %s
        """,
        (snapshot_id,),
    ).fetchone()
    if row is None:
        return None
    return SourceSnapshot(
        id=row[0],
        url=row[1],
        body=row[2],
        response_status=row[3],
        retrieved_at=row[4],
        parser_version=row[5],
    )


def publish(
    conn: psycopg.Connection,
    record: Opportunity,
    report: ValidationReport,
    snapshots: Sequence[SourceSnapshot],
    *,
    policy_version: str = POLICY_VERSION,
    approved_hosts: Sequence[str] = APPROVED_SOURCE_HOSTS,
) -> PublishedRevision:
    """Publish one revision or raise ``PublicationBlocked`` without writing.

    The review findings are loaded from their register here, so the decision
    always accounts for a recorded discrepancy.
    """

    by_id: dict[str, SourceSnapshot] = {}
    for snapshot in snapshots:
        if snapshot.id in by_id:
            raise ValueError(f"snapshot {snapshot.id} was supplied twice")
        by_id[snapshot.id] = snapshot

    decision = evaluate(
        record,
        report,
        by_id,
        register=load_register(),
        policy_version=policy_version,
        approved_hosts=approved_hosts,
    )
    if decision.decision is not DecisionType.PUBLISH:
        raise PublicationBlocked(decision)

    digest = content_hash(record)
    with conn.transaction():
        conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (record.id,))
        for snapshot in snapshots:
            _store_snapshot(conn, snapshot)
        _require_retained_content(conn, decision, by_id)
        write_payload(conn, record)
        revision = _write_revision(conn, record, report, decision, digest)
        conn.execute(
            """
            UPDATE publication_state
            SET assurance = 'source_checked',
                source_checked_at = (SELECT checked_at FROM opportunity_revisions WHERE opportunity_id = %s AND revision = %s),
                validation_policy_version = %s,
                freshness = 'current',
                revision = %s
            WHERE opportunity_id = %s
            """,
            (record.id, revision, decision.policy_version, revision, record.id),
        )

    return PublishedRevision(
        opportunity_id=record.id,
        revision=revision,
        content_hash=digest,
        decision=decision,
    )


def _require_retained_content(
    conn: psycopg.Connection,
    decision: PublicationDecision,
    by_id: dict[str, SourceSnapshot],
) -> None:
    """Refuse to publish against snapshots the database does not hold as checked."""

    for snapshot_id in decision.snapshot_ids:
        row = conn.execute(
            "SELECT content_hash FROM source_snapshots WHERE id = %s", (snapshot_id,)
        ).fetchone()
        if row is None:
            raise SnapshotConflict(f"snapshot {snapshot_id} was not retained")
        if row[0] != by_id[snapshot_id].content_hash:
            raise SnapshotConflict(
                f"retained snapshot {snapshot_id} does not match the checked content"
            )


def _write_revision(
    conn: psycopg.Connection,
    record: Opportunity,
    report: ValidationReport,
    decision: PublicationDecision,
    digest: str,
) -> int:
    """Insert an immutable revision, reusing the latest one for identical facts."""

    latest = conn.execute(
        """
        SELECT revision, content_hash, report FROM opportunity_revisions
        WHERE opportunity_id = %s ORDER BY revision DESC LIMIT 1
        """,
        (record.id,),
    ).fetchone()
    if latest is not None and latest[1] == digest and {k:v for k,v in latest[2].items() if k != "checked_at"} == report.model_dump(mode="json", by_alias=False, exclude={"checked_at"}):
        return int(latest[0])

    revision = (int(latest[0]) if latest is not None else 0) + 1
    conn.execute(
        """
        INSERT INTO opportunity_revisions
            (opportunity_id, revision, content_hash, payload, policy_version,
             checked_at, report)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            record.id,
            revision,
            digest,
            Jsonb(record.model_dump(mode="json", by_alias=False)),
            decision.policy_version,
            report.checked_at,
            Jsonb(report.model_dump(mode="json", by_alias=False)),
        ),
    )
    for snapshot_id in decision.snapshot_ids:
        conn.execute(
            """
            INSERT INTO revision_snapshots (opportunity_id, revision, snapshot_id)
            VALUES (%s, %s, %s)
            """,
            (record.id, revision, snapshot_id),
        )
    return revision
