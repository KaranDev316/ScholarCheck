"""S01 assurance metadata must not claim a check that did not happen."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.opportunity import PublicationMetadata

CHECKED_AT = datetime(2026, 10, 23, 7, 30, tzinfo=UTC)


def test_fixture_metadata_is_honestly_unchecked() -> None:
    metadata = PublicationMetadata(
        assurance="insufficient_evidence",
        freshness="not_checked",
    )
    assert metadata.source_checked_at is None
    assert metadata.validation_policy_version is None


@pytest.mark.parametrize(
    ("assurance", "checked_at", "policy_version"),
    [
        ("insufficient_evidence", CHECKED_AT, None),
        ("insufficient_evidence", None, "1.0"),
        ("source_checked", None, "1.0"),
        ("source_checked", CHECKED_AT, None),
    ],
)
def test_partial_or_false_source_check_is_rejected(
    assurance: str, checked_at: datetime | None, policy_version: str | None
) -> None:
    with pytest.raises(ValidationError):
        PublicationMetadata(
            assurance=assurance,
            source_checked_at=checked_at,
            validation_policy_version=policy_version,
            freshness="current",
        )


def test_checked_timestamp_requires_timezone() -> None:
    with pytest.raises(ValidationError):
        PublicationMetadata(
            assurance="source_checked",
            source_checked_at=datetime(2026, 10, 23, 7, 30),
            validation_policy_version="1.0",
            freshness="current",
        )
