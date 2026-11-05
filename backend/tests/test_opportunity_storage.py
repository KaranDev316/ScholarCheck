"""T04-T05: real PostgreSQL fixture loading and read endpoint.

Set SCHOLARCHECK_TEST_DATABASE_URL to a disposable PostgreSQL database to run
these integration tests. Each test creates and drops its own schema.
"""

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.publication.store import publish
from app.storage.opportunities import (
    CONTENT_DIR,
    get_opportunity,
    load_seed,
    read_seed,
)
from tests.publication_helpers import build_report, build_snapshots, sample_record


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


def test_t04_loader_refuses_to_overwrite_a_published_record(test_dsn: str) -> None:
    candidate = sample_record()
    snapshots = build_snapshots(candidate)
    with psycopg.connect(test_dsn) as conn:
        publish(
            conn,
            candidate,
            build_report(candidate, snapshots),
            snapshots,
            approved_hosts=("nserc-crsng.canada.ca",),
        )
        with pytest.raises(ValueError, match="cannot overwrite"):
            load_seed(conn, candidate)


def test_t05_dev_read_is_honest_and_production_hides_unpublished(test_dsn: str) -> None:
    seed = read_seed(CONTENT_DIR / "udem-exemption-doctoral.yaml")
    with psycopg.connect(test_dsn) as conn:
        load_seed(conn, seed)

    with TestClient(create_app(settings_for(test_dsn))) as client:
        response = client.get(f"/api/v1/opportunities/{seed.id}")
        assert response.status_code == 404
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
