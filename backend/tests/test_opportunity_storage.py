"""T04-T05: real PostgreSQL fixture loading and read endpoint.

Set SCHOLARCHECK_TEST_DATABASE_URL to a disposable PostgreSQL database to run
these integration tests. Each test creates and drops its own schema.
"""

import os
from collections.abc import Iterator
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg import sql
from psycopg.conninfo import make_conninfo

from app.config import Settings
from app.main import create_app
from app.storage.opportunities import (
    CONTENT_DIR,
    create_schema,
    get_opportunity,
    load_seed,
    read_seed,
)


@pytest.fixture
def test_dsn() -> Iterator[str]:
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


def settings_for(dsn: str | None, environment: str = "test") -> Settings:
    return Settings(
        app_env=environment,
        cors_allowed_origins=("http://localhost:5173",),
        database_url=dsn,
    )


def test_t04_all_fixtures_load_idempotently_and_round_trip(test_dsn: str) -> None:
    seeds = [read_seed(path) for path in sorted(CONTENT_DIR.glob("*.yaml"))]
    assert len(seeds) == 4

    with psycopg.connect(test_dsn) as conn:
        assert all(load_seed(conn, seed) for seed in seeds)
        assert not any(load_seed(conn, seed) for seed in seeds)
        assert conn.execute("SELECT count(*) FROM opportunities").fetchone()[0] == 4
        for seed in seeds:
            result = get_opportunity(conn, seed.id)
            assert result is not None
            restored, metadata = result
            assert restored == seed
            assert metadata == {
                "assurance": "insufficient_evidence",
                "source_checked_at": None,
                "validation_policy_version": None,
                "freshness": "not_checked",
            }
        assert get_opportunity(conn, "missing-opportunity") is None


def test_t04_loader_refuses_to_overwrite_checked_record(test_dsn: str) -> None:
    seed = read_seed(CONTENT_DIR / "cgsd-doctoral.yaml")
    with psycopg.connect(test_dsn) as conn:
        assert load_seed(conn, seed)
        conn.execute(
            """
            UPDATE publication_state SET assurance = 'source_checked',
                source_checked_at = now(), validation_policy_version = '1.0',
                freshness = 'current'
            WHERE opportunity_id = %s
            """,
            (seed.id,),
        )
        conn.commit()
        with pytest.raises(ValueError, match="cannot overwrite"):
            load_seed(conn, seed)


def test_t05_dev_read_is_honest_and_production_hides_unpublished(test_dsn: str) -> None:
    seed = read_seed(CONTENT_DIR / "udem-exemption-doctoral.yaml")
    with psycopg.connect(test_dsn) as conn:
        load_seed(conn, seed)

    with TestClient(create_app(settings_for(test_dsn))) as client:
        response = client.get(f"/api/v1/opportunities/{seed.id}")
        assert response.status_code == 200
        body = response.json()
        assert body["opportunity"]["id"] == seed.id
        assert body["opportunity"]["fundingComponents"][0]["amount"] == "24067.80"
        assert body["opportunity"]["evidence"][0]["verifiedAt"] is None
        assert body["publication"] == {
            "assurance": "insufficient_evidence",
            "sourceCheckedAt": None,
            "validationPolicyVersion": None,
            "freshness": "not_checked",
        }
        assert body["isPublished"] is False
        missing = client.get("/api/v1/opportunities/unknown-id")
        assert missing.status_code == 404
        assert missing.json()["code"] == "opportunity_not_found"

    with TestClient(create_app(settings_for(test_dsn, "production"))) as client:
        hidden = client.get(f"/api/v1/opportunities/{seed.id}")
        assert hidden.status_code == 404
        assert hidden.json()["code"] == "opportunity_not_found"


def test_t05_read_without_database_uses_structured_503() -> None:
    with TestClient(create_app(settings_for(None))) as client:
        response = client.get("/api/v1/opportunities/any-id")
    assert response.status_code == 503
    assert response.json()["code"] == "service_unavailable"
