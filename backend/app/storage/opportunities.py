"""Repeatable seed loading and read-only opportunity reconstruction.

The fixture loader never grants publication assurance. It refuses to overwrite
an already source-checked record; future publishing uses a separate revision
path with its own validation report and evidence snapshots.
"""

import hashlib
import json
from pathlib import Path

import psycopg
import yaml
from psycopg.types.json import Jsonb

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
    """Create S01 tables; safe to call again on the same database."""
    with conn.transaction():
        conn.execute(SCHEMA_PATH.read_text(encoding="utf-8"))


def read_seed(path: Path) -> Opportunity:
    """Validate one YAML file using the same strict model as the API."""
    return Opportunity.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def load_seed(conn: psycopg.Connection, opportunity: Opportunity) -> bool:
    """Insert or update a fixture atomically; return False if unchanged."""
    payload = opportunity.model_dump(mode="json", by_alias=False)
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

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
            (opportunity.id, Jsonb(parent), digest),
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
