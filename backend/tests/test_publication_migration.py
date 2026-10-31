"""Migration tests for the publication schema.

A database created before the gate has a ``human_verified`` assurance level
and a source-check flag with nothing behind it. Opening the schema must remove
the level, demote those rows, and refuse them afterwards.
"""

import psycopg
import pytest

from app.storage.opportunities import create_schema

LEGACY_SCHEMA = """
CREATE TABLE opportunities (
    id text PRIMARY KEY,
    payload jsonb NOT NULL,
    content_hash text NOT NULL,
    loaded_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE publication_state (
    opportunity_id text PRIMARY KEY REFERENCES opportunities(id) ON DELETE CASCADE,
    assurance text NOT NULL DEFAULT 'insufficient_evidence'
        CHECK (assurance IN ('insufficient_evidence', 'source_checked', 'human_verified')),
    source_checked_at timestamptz,
    validation_policy_version text,
    freshness text NOT NULL DEFAULT 'not_checked'
        CHECK (freshness IN ('not_checked', 'current', 'needs_recheck', 'stale')),
    CHECK (
        (assurance = 'insufficient_evidence' AND source_checked_at IS NULL
            AND validation_policy_version IS NULL)
        OR (assurance IN ('source_checked', 'human_verified')
            AND source_checked_at IS NOT NULL
            AND validation_policy_version IS NOT NULL)
    )
);
"""


def _install_legacy_state(conn: psycopg.Connection) -> None:
    conn.execute(
        """
        DROP TABLE IF EXISTS revision_snapshots, opportunity_revisions,
            publication_state, opportunities CASCADE
        """
    )
    conn.execute(LEGACY_SCHEMA)
    conn.execute(
        """
        INSERT INTO opportunities (id, payload, content_hash)
        VALUES ('legacy-human', '{}', 'x'), ('legacy-checked', '{}', 'y')
        """
    )
    conn.execute(
        """
        INSERT INTO publication_state
            (opportunity_id, assurance, source_checked_at,
             validation_policy_version, freshness)
        VALUES
            ('legacy-human', 'human_verified', now(), '0.pre-gate', 'current'),
            ('legacy-checked', 'source_checked', now(), '0.pre-gate', 'current')
        """
    )


def _state(conn: psycopg.Connection, opportunity_id: str):
    return conn.execute(
        """
        SELECT assurance, source_checked_at, validation_policy_version,
               freshness, revision
        FROM publication_state WHERE opportunity_id = %s
        """,
        (opportunity_id,),
    ).fetchone()


def test_legacy_assurance_is_demoted_and_human_verified_is_gone(test_dsn: str) -> None:
    with psycopg.connect(test_dsn) as conn:
        _install_legacy_state(conn)
        create_schema(conn)

        for opportunity_id in ("legacy-human", "legacy-checked"):
            state = _state(conn, opportunity_id)
            assert state == ("insufficient_evidence", None, None, "needs_recheck", None)


def test_the_migrated_database_rejects_human_verified(test_dsn: str) -> None:
    with psycopg.connect(test_dsn) as conn:
        _install_legacy_state(conn)
        create_schema(conn)

    with psycopg.connect(test_dsn) as conn:
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute(
                "UPDATE publication_state SET assurance = 'human_verified', "
                "source_checked_at = now(), validation_policy_version = 'x' "
                "WHERE opportunity_id = 'legacy-human'"
            )


def test_opening_the_schema_twice_is_a_no_op(test_dsn: str) -> None:
    with psycopg.connect(test_dsn) as conn:
        create_schema(conn)
        create_schema(conn)
        assert conn.execute("SELECT count(*) FROM publication_state").fetchone()[0] == 0
