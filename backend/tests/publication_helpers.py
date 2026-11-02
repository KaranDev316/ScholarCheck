"""Build retained snapshots and validation reports for tests.

Snapshots are assembled from a record's own evidence, so a test can state
exactly which page is retained and which passage is missing. Nothing here
publishes: the gate and the store under test make that decision.
"""

import hashlib
import json
import re
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.domain.enums import (
    FundingComponentKind,
    FundingRelationship,
    FundingStatus,
)
from app.domain.hashing import content_hash
from app.domain.models import Evidence, FundingComponent, OfficialLinks, Opportunity
from app.publication.contracts import (
    CheckResult,
    ClaimCheck,
    SourceSnapshot,
    ValidationReport,
)
from app.publication.policy import POLICY_VERSION
from app.publication.register import REGISTER_PATH, Finding, FindingsRegister

CHECKED_AT = datetime(2026, 10, 31, 9, 0, tzinfo=UTC)
RETRIEVED_AT = datetime(2026, 10, 30, 8, 0, tzinfo=UTC)
PARSER_VERSION = "test-extraction/1"
SAMPLE_URL = (
    "https://nserc-crsng.canada.ca/en/funding-opportunity/sample-award"
)
SAMPLE_PASSAGE = "The scholarship pays $40,000 per year for 36 months."
FINDINGS_PATH = REGISTER_PATH


def no_findings() -> FindingsRegister:
    """A register with nothing outstanding, for records under review nowhere."""

    return FindingsRegister()


def held_register(
    opportunity_id: str,
    evidence_id: str,
    url: str,
    reason: str,
    *,
    result: CheckResult = CheckResult.UNCLEAR,
) -> FindingsRegister:
    """A register recording one open finding against one record and page."""

    return FindingsRegister(
        entries={
            opportunity_id: (
                Finding(
                    evidence_id=evidence_id,
                    evidence_url=url,
                    result=result,
                    reason=reason,
                ),
            )
        }
    )


def sample_record(
    *,
    evidence: tuple[Evidence, ...] | None = None,
    components: tuple[FundingComponent, ...] | None = None,
) -> Opportunity:
    """A minimal candidate whose stated amount appears in its cited passage."""

    entries = evidence or (
        Evidence(
            id="ev-value",
            url=SAMPLE_URL,
            passage=SAMPLE_PASSAGE,
            retrieved_at=RETRIEVED_AT,
        ),
    )
    return Opportunity(
        id="gate-sample",
        scheme_name="Gate sample award",
        funder="Example government",
        destinations=("CA",),
        summary="A record used to exercise the publication gate.",
        links=OfficialLinks(
            summary_url=SAMPLE_URL,
            requirements_url=f"{SAMPLE_URL}#eligibility",
            portal_url=f"{SAMPLE_URL}/apply",
        ),
        funding_components=components
        or (
            FundingComponent(
                id="fund-living",
                kind=FundingComponentKind.LIVING_SUPPORT,
                status=FundingStatus.SPECIFIED,
                relationship=FundingRelationship.GRANT,
                description="Annual stipend.",
                amount=Decimal("40000"),
                currency="CAD",
                period="per year",
                evidence_refs=("ev-value",),
            ),
        ),
        evidence=entries,
        last_retrieved_at=RETRIEVED_AT,
    )


def snapshot_id(url: str) -> str:
    """A stable, readable snapshot id derived from the page address.

    The short hash keeps two long addresses on the same site distinct; a plain
    slug truncates at the shared prefix and would collide.
    """

    slug = re.sub(r"[^a-z0-9]+", "-", url.lower().removeprefix("https://")).strip("-")
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    return f"snap-{slug[:60].strip('-')}-{digest}"


def build_snapshots(
    record: Opportunity,
    *,
    omit: tuple[str, ...] = (),
    body_suffix: str = "",
) -> tuple[SourceSnapshot, ...]:
    """One retained snapshot per cited page, holding that page's passages."""

    pages: dict[str, list[str]] = {}
    retrieved: dict[str, datetime] = {}
    for entry in record.evidence:
        if entry.id in omit:
            continue
        url = str(entry.url)
        pages.setdefault(url, []).append(entry.passage)
        retrieved[url] = entry.retrieved_at

    return tuple(
        SourceSnapshot(
            id=snapshot_id(url),
            url=url,
            body="\n\n".join(parts) + body_suffix,
            retrieved_at=retrieved[url],
            parser_version=PARSER_VERSION,
        )
        for url, parts in pages.items()
    )


def build_report(
    record: Opportunity,
    snapshots: tuple[SourceSnapshot, ...],
    *,
    results: dict[str, CheckResult] | None = None,
    reasons: dict[str, str] | None = None,
    excerpts: dict[str, str] | None = None,
    policy_version: str = POLICY_VERSION,
) -> ValidationReport:
    """A report claiming support for every evidence entry a snapshot covers."""

    by_url = {str(snapshot.url): snapshot for snapshot in snapshots}
    checks = []
    for entry in record.evidence:
        snapshot = by_url.get(str(entry.url))
        if snapshot is None:
            continue
        checks.append(
            ClaimCheck(
                claim=f"{entry.id} passage",
                evidence_id=entry.id,
                snapshot_id=snapshot.id,
                excerpt=(excerpts or {}).get(entry.id, entry.passage),
                result=(results or {}).get(entry.id, CheckResult.SUPPORTED),
                reason=(reasons or {}).get(entry.id),
            )
        )
    if not checks:
        raise AssertionError(f"no snapshot covers {record.id}")
    return ValidationReport(
        opportunity_id=record.id,
        content_hash=content_hash(record),
        policy_version=policy_version,
        checked_at=CHECKED_AT,
        checks=tuple(checks),
    )


def load_findings() -> dict[str, Any]:
    """The recorded first-pass findings that keep fixtures held."""

    return json.loads(FINDINGS_PATH.read_text(encoding="utf-8"))
