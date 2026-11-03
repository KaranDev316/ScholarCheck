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
    Applicability,
    CheckResult,
    ClaimCheck,
    SourceSnapshot,
    ValidationReport,
)
from app.publication.facts import (
    FactReading,
    FactState,
    MaterialFact,
    MaterialFactKind,
    MaterialFacts,
    subject,
)
from app.publication.gates import digits_only
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


def build_facts(
    record: Opportunity,
    *,
    excerpts: dict[str, str] | None = None,
) -> MaterialFacts:
    """One fact per decision-critical field, read from the record's citations.

    A field the record displays is stated with a passage the record cites for
    it, so the gate can compare the two. A field the seed does not publish — a
    rate year, or a dated deadline — is recorded as unspecified with the reason,
    because inventing a reading for it would be exactly what the fact table
    exists to prevent. Support for each stated fact is decided in
    ``build_report``, not here.
    """

    overrides = excerpts or {}
    facts: list[MaterialFact] = []
    for component in record.funding_components:
        prefix = subject("component", component.id)
        facts.append(
            _fact(
                record,
                prefix,
                MaterialFactKind.AMOUNT,
                None if component.amount is None else f"{component.amount:f}",
                component.evidence_refs,
                overrides,
                "the record publishes no amount for this component",
            )
        )
        facts.append(
            _fact(
                record,
                prefix,
                MaterialFactKind.CURRENCY,
                component.currency,
                component.evidence_refs,
                overrides,
                "the record publishes no currency for this component",
            )
        )
        facts.append(
            _fact(
                record,
                prefix,
                MaterialFactKind.FUNDING_RELATIONSHIP,
                None
                if component.relationship is FundingRelationship.NOT_STATED
                else component.relationship.value,
                component.evidence_refs,
                overrides,
                "the record publishes no funding relationship for this component",
            )
        )
        facts.append(
            _fact(
                record,
                prefix,
                MaterialFactKind.RATE_YEAR,
                None,
                component.evidence_refs,
                overrides,
                "the record publishes no rate year for this component",
            )
        )
    for round_entry in record.rounds:
        prefix = subject("round", round_entry.id)
        facts.append(
            _fact(
                record,
                prefix,
                MaterialFactKind.INTAKE,
                round_entry.intake,
                (),
                overrides,
                "the round is published without a dated intake",
            )
        )
        facts.append(
            _fact(
                record,
                prefix,
                MaterialFactKind.APPLICATION_ROUTE,
                round_entry.route,
                (),
                overrides,
                "the round is published without an application route",
            )
        )
        facts.append(
            _fact(
                record,
                prefix,
                MaterialFactKind.DEADLINE,
                None,
                (),
                overrides,
                "the seed keeps this round's dates in its label, not as a dated fact",
            )
        )
        facts.append(
            _fact(
                record,
                prefix,
                MaterialFactKind.STAGE,
                None,
                (),
                overrides,
                "the seed does not say which stage this round's date belongs to",
            )
        )
    for rule in record.eligibility_rules:
        facts.append(
            _fact(
                record,
                subject("rule", rule.id),
                MaterialFactKind.ELIGIBILITY_RESTRICTION,
                rule.requirement if rule.evidence_refs else None,
                rule.evidence_refs,
                overrides,
                "the record states this requirement without a citation",
            )
        )
    return MaterialFacts(facts=tuple(facts))


def _fact(
    record: Opportunity,
    prefix: str,
    kind: MaterialFactKind,
    value: str | None,
    evidence_ids: tuple[str, ...],
    overrides: dict[str, str],
    reason: str,
) -> MaterialFact:
    if value is None:
        return MaterialFact(
            kind=kind,
            subject=prefix,
            state=FactState.UNSPECIFIED,
            reason=reason,
        )
    entry = _reading_entry(record, value, evidence_ids)
    return MaterialFact(
        kind=kind,
        subject=prefix,
        state=FactState.STATED,
        value=value,
        readings=(
            FactReading(
                value=value,
                evidence_id=entry.id,
                snapshot_id=snapshot_id(str(entry.url)),
                excerpt=overrides.get(entry.id, entry.passage),
            ),
        ),
    )


def _reading_entry(
    record: Opportunity, value: str, evidence_ids: tuple[str, ...]
) -> Evidence:
    """The cited page that reads the value, or the first page the record cites."""

    cited = [entry for entry in record.evidence if entry.id in evidence_ids]
    pool = cited or list(record.evidence)
    digits = digits_only(value)
    if digits:
        matches = [entry for entry in pool if digits in digits_only(entry.passage)]
    else:
        matches = [entry for entry in pool if value.casefold() in entry.passage.casefold()]
    return (matches or pool)[0]


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
