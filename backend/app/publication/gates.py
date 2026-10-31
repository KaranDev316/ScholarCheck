"""The deterministic publication gate.

One pure function decides whether a candidate may become public. It enforces
the checks that must not depend on a model's judgement: the report must belong
to this exact revision and policy version, every claim must cite a retained
snapshot from an approved provider, every excerpt and every displayed passage
must still occur in that snapshot, every evidence entry must be covered, and
every stated amount must appear in the passage that backs it.

A failed check produces a ``hold`` (evidence is missing, unclear or
inconsistent) or a ``reject`` (identity, source or citation is invalid). Either
way no record becomes public: ``store.publish`` raises before writing. A
candidate with an open review finding is always held, even if its report claims
support for every entry, so a known discrepancy cannot be papered over.

Nothing here can be satisfied by a confidence score or by a person's approval.
"""

from collections.abc import Mapping, Sequence
from decimal import Decimal

from app.domain.enums import PublicationAssurance
from app.domain.hashing import content_hash
from app.domain.models import Opportunity
from app.publication.contracts import (
    CheckResult,
    DecisionType,
    PublicationDecision,
    SourceSnapshot,
    ValidationReport,
)
from app.publication.policy import (
    APPROVED_SOURCE_HOSTS,
    POLICY_VERSION,
    is_approved_source,
    source_host,
)


class PublicationBlocked(Exception):
    """Raised when a candidate may not become public; carries the decision."""

    def __init__(self, decision: PublicationDecision) -> None:
        self.decision = decision
        super().__init__(f"{decision.decision.value}: {'; '.join(decision.reasons)}")


def normalise(text: str) -> str:
    """Collapse whitespace runs so layout differences do not fake a match."""

    return " ".join(text.split())


def excerpt_in_text(text: str, excerpt: str) -> bool:
    """Exact wording match after whitespace collapsing; no fuzzy tolerance."""

    return normalise(excerpt) in normalise(text)


def digits_only(text: str) -> str:
    """Keep digits only, so 24 067,80 and 24,067.80 compare alike."""

    return "".join(character for character in text if character.isdigit())


def amount_in_text(amount: Decimal, text: str) -> bool:
    """True when the published amount's digits occur in the given text."""

    wanted = digits_only(f"{amount:f}")
    return bool(wanted) and wanted in digits_only(text)


def evaluate(
    record: Opportunity,
    report: ValidationReport,
    snapshots: Mapping[str, SourceSnapshot],
    *,
    policy_version: str = POLICY_VERSION,
    approved_hosts: Sequence[str] = APPROVED_SOURCE_HOSTS,
    open_findings: Sequence[str] = (),
) -> PublicationDecision:
    """Decide publish, hold or reject for one candidate revision."""

    rejected: list[str] = []
    held: list[str] = []

    for finding in open_findings:
        held.append(f"open review finding: {normalise(finding)}")

    if report.opportunity_id != record.id:
        rejected.append(f"report is for {report.opportunity_id}, not {record.id}")
    if report.content_hash != content_hash(record):
        rejected.append("report was written for a different revision of the record")
    if report.policy_version != policy_version:
        held.append(
            f"report was produced under policy {report.policy_version}; "
            f"the gate runs {policy_version}"
        )

    evidence_by_id = {entry.id: entry for entry in record.evidence}
    covered: dict[str, SourceSnapshot] = {}
    cited: dict[str, str] = {}
    hosts = tuple(approved_hosts)

    for check in report.checks:
        label = f"{check.claim} ({check.evidence_id})"
        snapshot = snapshots.get(check.snapshot_id)
        if snapshot is None:
            held.append(f"{label}: snapshot {check.snapshot_id} was not retained")
            continue
        if not is_approved_source(snapshot.url, hosts):
            rejected.append(
                f"{label}: {source_host(snapshot.url)} is not an approved provider"
            )

        evidence = evidence_by_id.get(check.evidence_id)
        if evidence is None:
            rejected.append(
                f"{label}: the report cites evidence that is not on the record"
            )
            continue
        if evidence.url != snapshot.url:
            held.append(f"{label}: the citation and its snapshot are different pages")
        else:
            covered[evidence.id] = snapshot
        if evidence.retrieved_at != snapshot.retrieved_at:
            held.append(f"{label}: the snapshot was retrieved at a different time")

        if check.result is not CheckResult.SUPPORTED:
            reason = f": {check.reason}" if check.reason else ""
            held.append(
                f"{label}: the evidence check returned {check.result.value}{reason}"
            )
        if not excerpt_in_text(snapshot.body, check.excerpt):
            held.append(f"{label}: the quoted excerpt is not in the retained snapshot")

        previous = cited.get(check.evidence_id)
        if previous is not None and previous != check.excerpt:
            held.append(f"{label}: two different excerpts cite one claim")
        else:
            cited[check.evidence_id] = check.excerpt

    for evidence in record.evidence:
        snapshot = covered.get(evidence.id)
        if evidence.id not in cited:
            held.append(f"{evidence.id}: no evidence check covers this claim")
        elif snapshot is not None and not excerpt_in_text(
            snapshot.body, evidence.passage
        ):
            held.append(f"{evidence.id}: the displayed passage is not in its snapshot")

    for component in record.funding_components:
        if component.amount is None:
            continue
        if not component.evidence_refs:
            held.append(f"{component.id}: an amount is stated without evidence")
            continue
        excerpts = [
            check.excerpt
            for check in report.checks
            if check.evidence_id in component.evidence_refs
        ]
        if not excerpts:
            held.append(f"{component.id}: no evidence check backs its amount")
        elif not any(amount_in_text(component.amount, excerpt) for excerpt in excerpts):
            held.append(
                f"{component.id}: the amount {component.amount:f} is not stated "
                "in the passage that backs it"
            )

    if rejected:
        decision = DecisionType.REJECT
    elif held:
        decision = DecisionType.HOLD
    else:
        decision = DecisionType.PUBLISH

    return PublicationDecision(
        opportunity_id=record.id,
        decision=decision,
        assurance=(
            PublicationAssurance.SOURCE_CHECKED
            if decision is DecisionType.PUBLISH
            else PublicationAssurance.INSUFFICIENT_EVIDENCE
        ),
        policy_version=policy_version,
        checked_at=report.checked_at,
        snapshot_ids=tuple(sorted({check.snapshot_id for check in report.checks})),
        reasons=tuple(rejected + held),
    )
