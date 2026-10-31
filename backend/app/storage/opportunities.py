"""Repeatable seed loading and read-only opportunity reconstruction.

The fixture loader never grants publication assurance. It refuses to overwrite
an already published record; publishing goes through
``app.publication.store.publish``, which requires a validation report and the
retained snapshots it checked.
"""

from pathlib import Path

import psycopg
import yaml
from psycopg.types.json import Jsonb

from app.domain.hashing import content_hash
from app.domain.models import Opportunity

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
CONTENT_DIR = Path(__file__).resolve().parents[3] / "content" / "opportunities"

CHILDREN = {
    "programmes": "programmes",
    "rounds": "rounds",
    "eligibility_rules": "eligibility_rules",
    "funding_components": "funding_components",
    "evidence": "evidence",
}


def create_schema(conn: psycopg.Connection) -> None:
    """Create S01 tables and apply migrations; safe to call on an existing database."""

    with conn.transaction():
        conn.execute(SCHEMA_PATH.read_text(encoding="utf-8"))


def read_seed(path: Path) -> Opportunity:
    """Validate one YAML file using the same strict model as the API."""
    return Opportunity.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def write_payload(conn: psycopg.Connection, opportunity: Opportunity) -> None:
    """Insert or replace the live facts for one opportunity.

    The caller owns the transaction: the fixture loader and the publication
    gate both use this writer, and the gate must be able to roll a whole
    publish back.
    """

    payload = opportunity.model_dump(mode="json", by_alias=False)
    parent = {key: value for key, value in payload.items() if key not in CHILDREN}
    conn.execute(
        """
        INSERT INTO opportunities (id, payload, content_hash)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET payload = EXCLUDED.payload,
            content_hash = EXCLUDED.content_hash,
            loaded_at = now()
        """,
        (opportunity.id, Jsonb(parent), content_hash(opportunity)),
    )
    conn.execute(
        """
        INSERT INTO publication_state (opportunity_id)
        VALUES (%s) ON CONFLICT (opportunity_id) DO NOTHING
        """,
        (opportunity.id,),
    )
    for table, field in CHILDREN.items():
        # Table names are constants defined above, never request input.
        conn.execute(f"DELETE FROM {table} WHERE opportunity_id = %s", (opportunity.id,))
        for position, child in enumerate(payload[field]):
            conn.execute(
                f"""
                INSERT INTO {table} (opportunity_id, id, position, payload)
                VALUES (%s, %s, %s, %s)
                """,
                (opportunity.id, child["id"], position, Jsonb(child)),
            )


def load_seed(conn: psycopg.Connection, opportunity: Opportunity) -> bool:
    """Insert or update a fixture atomically; return False if unchanged."""

    digest = content_hash(opportunity)
    with conn.transaction():
        row = conn.execute(
            """
            SELECT o.content_hash, s.assurance
            FROM opportunities AS o
            JOIN publication_state AS s ON s.opportunity_id = o.id
            WHERE o.id = %s FOR UPDATE OF o, s
            """,
            (opportunity.id,),
        ).fetchone()
        if row and row[1] != "insufficient_evidence":
            raise ValueError("fixture import cannot overwrite a published opportunity")
        if row and row[0] == digest:
            return False
        write_payload(conn, opportunity)
    return True


def get_opportunity(
    conn: psycopg.Connection, opportunity_id: str
) -> tuple[Opportunity, dict[str, object]] | None:
    """Read all child collections in their seed order with assurance metadata."""
    row = conn.execute(
        """
        SELECT o.payload, s.assurance, s.source_checked_at,
               s.validation_policy_version, s.freshness
        FROM opportunities AS o
        JOIN publication_state AS s ON s.opportunity_id = o.id
        WHERE o.id = %s
        """,
        (opportunity_id,),
    ).fetchone()
    if row is None:
        return None

    payload = dict(row[0])
    for table, field in CHILDREN.items():
        payload[field] = [
            child_row[0]
            for child_row in conn.execute(
                f"SELECT payload FROM {table} WHERE opportunity_id = %s ORDER BY position",
                (opportunity_id,),
            )
        ]
    metadata = {
        "assurance": row[1],
        "source_checked_at": row[2],
        "validation_policy_version": row[3],
        "freshness": row[4],
    }
    return Opportunity.model_validate(payload), metadata
