"""The deterministic publication gate.

One pure function decides whether a candidate may become public. It enforces
the checks that must not depend on a model's judgement: the report must belong
to this exact revision and policy version, every claim must cite a retained
snapshot from an approved provider, every excerpt and every displayed passage
must still occur in that snapshot, every evidence entry must be covered, and
every stated amount must appear in the passage that backs it.

The report also carries the candidate's material-fact table. The gate requires a
fact for every decision-critical field, re-checks each fact's own reading against
the snapshot it names, refuses a fact the record contradicts, and counts a fact
as covered only when a supported check quotes one of its spans. A record
therefore cannot display an amount, a currency, a route or an intake that its
fact table does not state, and cannot state one its pages do not back.

A failed check produces a ``hold`` (evidence is missing, unclear or
inconsistent) or a ``reject`` (identity, source or citation is invalid). Either
way no record becomes public: ``store.publish`` raises before writing. A
candidate with an open review finding is always held, even if its report claims
support for every entry, so a known discrepancy cannot be papered over.

The findings come from a ``FindingsRegister`` the caller must supply: the
parameter has no default, and ``store.publish`` reads the register from disk
itself rather than accepting one. A publisher therefore cannot omit the findings
it does not like.

Nothing here can be satisfied by a confidence score or by a person's approval.
"""

from collections.abc import Mapping, Sequence
from decimal import Decimal

from app.domain.enums import FundingRelationship, PublicationAssurance
from app.domain.hashing import content_hash
from app.domain.models import Evidence, Opportunity
from app.publication.contracts import (
    CheckResult,
    ClaimCheck,
    DecisionType,
    PublicationDecision,
    SourceSnapshot,
    ValidationReport,
)
from app.publication.facts import (
    FactState,
    MaterialFact,
    MaterialFactKind,
    MaterialFacts,
    required_fact_keys,
    subject,
)
from app.publication.policy import (
    APPROVED_SOURCE_HOSTS,
    POLICY_VERSION,
    is_approved_source,
    source_host,
)
from app.publication.register import FindingsRegister


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
    register: FindingsRegister,
    policy_version: str = POLICY_VERSION,
    approved_hosts: Sequence[str] = APPROVED_SOURCE_HOSTS,
) -> PublicationDecision:
    """Decide publish, hold or reject for one candidate revision.

    ``register`` is required and has no default: a candidate with a recorded
    finding is held whatever its report says, and a register that could not be
    read holds everything.
    """

    rejected: list[str] = []
    held: list[str] = list(register.holds(record))

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
    excerpts_by_claim: dict[tuple[str, str | None], str] = {}
    cited: set[str] = set()
    hosts = tuple(approved_hosts)
    subjects = _subjects_on_record(record)

    for key in required_fact_keys(record):
        if report.facts.find(key) is None:
            held.append(f"{key}: the candidate records no material fact for this field")
    for fact in report.facts.facts:
        if fact.subject not in subjects:
            rejected.append(
                f"{fact.key}: the record has no {fact.subject} to state a fact about"
            )
        else:
            fact_rejected, fact_held = _fact_problems(
                fact, snapshots, evidence_by_id, hosts
            )
            rejected.extend(fact_rejected)
            held.extend(fact_held)

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

        cited.add(check.evidence_id)
        claim = (check.evidence_id, check.fact)
        previous = excerpts_by_claim.get(claim)
        if previous is not None and normalise(previous) != normalise(check.excerpt):
            held.append(f"{label}: two different excerpts cite one claim")
        else:
            excerpts_by_claim[claim] = check.excerpt
        held.extend(_verdict_problems(check, report.facts, record))

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

    settled = {
        (check.fact, check.snapshot_id)
        for check in report.checks
        if check.fact is not None and check.result is CheckResult.SUPPORTED
    }
    for fact in report.facts.stated:
        for reading in fact.readings:
            if (fact.key, reading.snapshot_id) not in settled:
                held.append(
                    f"{fact.key}: no supported check quotes the span from "
                    f"{reading.snapshot_id}"
                )
    held.extend(_record_fact_disagreements(record, report.facts))

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
        snapshot_ids=tuple(
            sorted(
                {check.snapshot_id for check in report.checks}
                | {
                    reading.snapshot_id
                    for fact in report.facts.facts
                    for reading in fact.readings
                }
            )
        ),
        reasons=tuple(rejected + held),
    )


def _subjects_on_record(record: Opportunity) -> set[str]:
    """Every subject a fact may be about, so a fact cannot name a missing part."""

    names = {subject("record")}
    for programme in record.programmes:
        names.add(subject("programme", programme.id))
    for round_entry in record.rounds:
        names.add(subject("round", round_entry.id))
    for component in record.funding_components:
        names.add(subject("component", component.id))
    for rule in record.eligibility_rules:
        names.add(subject("rule", rule.id))
    return names


def _fact_problems(
    fact: MaterialFact,
    snapshots: Mapping[str, SourceSnapshot],
    evidence_by_id: Mapping[str, Evidence],
    hosts: Sequence[str],
) -> tuple[list[str], list[str]]:
    """Re-check a fact's own readings against the pages it names."""

    rejected: list[str] = []
    held: list[str] = []
    for reading in fact.readings:
        snapshot = snapshots.get(reading.snapshot_id)
        if snapshot is None:
            held.append(f"{fact.key}: snapshot {reading.snapshot_id} was not retained")
            continue
        if not is_approved_source(snapshot.url, hosts):
            rejected.append(
                f"{fact.key}: {source_host(snapshot.url)} is not an approved provider"
            )
        evidence = evidence_by_id.get(reading.evidence_id)
        if evidence is None:
            rejected.append(
                f"{fact.key}: the fact reads from evidence that is not on the record"
            )
            continue
        if evidence.url != snapshot.url:
            held.append(f"{fact.key}: the reading and its snapshot are different pages")
        if evidence.retrieved_at != snapshot.retrieved_at:
            held.append(f"{fact.key}: the snapshot was retrieved at a different time")
        if not excerpt_in_text(snapshot.body, reading.excerpt):
            held.append(f"{fact.key}: the quoted span is not in the retained snapshot")
    if fact.kind is MaterialFactKind.AMOUNT and fact.value is not None:
        wanted = digits_only(fact.value)
        for reading in fact.readings:
            if not wanted or wanted not in digits_only(reading.excerpt):
                held.append(
                    f"{fact.key}: the amount {fact.value} is not stated in the span "
                    "that carries it"
                )
    return rejected, held


def _verdict_problems(
    check: ClaimCheck, facts: MaterialFacts, record: Opportunity
) -> list[str]:
    """A verdict must be about a stated fact and quote one of its spans."""

    if check.fact is None:
        if check.applies_to is not None:
            return [f"{check.claim}: applicability belongs to a material fact"]
        return []
    fact = facts.find(check.fact)
    if fact is None:
        return [f"{check.fact}: the report records no such material fact"]
    if fact.state is not FactState.STATED:
        return [f"{fact.key}: a {fact.state.value} fact has no claim to support"]
    problems: list[str] = []
    spans = [
        reading for reading in fact.readings if reading.snapshot_id == check.snapshot_id
    ]
    if not spans:
        problems.append(
            f"{fact.key}: no reading of this fact comes from snapshot "
            f"{check.snapshot_id}"
        )
    elif not any(
        normalise(reading.excerpt) == normalise(check.excerpt) for reading in spans
    ):
        problems.append(f"{fact.key}: the verdict quotes a span this fact does not carry")
    problems.extend(_applicability_problems(check, record))
    return problems


def _applicability_problems(check: ClaimCheck, record: Opportunity) -> list[str]:
    """The claim a span was applied to must be one this record actually makes."""

    applies_to = check.applies_to
    if applies_to is None:
        return []
    problems: list[str] = []
    round_ids = {round_entry.id for round_entry in record.rounds}
    levels = {programme.degree_level for programme in record.programmes}
    unknown = [round_id for round_id in applies_to.rounds if round_id not in round_ids]
    if unknown:
        problems.append(
            f"{check.claim}: the verdict places the quote in round {unknown[0]}, "
            "which the record does not have"
        )
    if applies_to.degree_level is not None and applies_to.degree_level not in levels:
        problems.append(
            f"{check.claim}: the verdict places the quote at "
            f"{applies_to.degree_level.value}, which the record does not offer"
        )
    about = (check.fact or "").partition(".")[0]
    if about.startswith("round:") and applies_to.rounds:
        own = about.split(":", 1)[1]
        if own not in applies_to.rounds:
            problems.append(
                f"{check.fact}: the quote is applied to "
                f"{', '.join(applies_to.rounds)} but states a fact about {own}"
            )
    return problems


def _displayed_facts(record: Opportunity) -> dict[str, str]:
    """The fields the record itself displays, keyed the way facts are keyed."""

    displayed: dict[str, str] = {}
    for component in record.funding_components:
        prefix = subject("component", component.id)
        if component.amount is not None:
            displayed[
                f"{prefix}.{MaterialFactKind.AMOUNT.value}"
            ] = f"{component.amount:f}"
        if component.currency is not None:
            displayed[f"{prefix}.{MaterialFactKind.CURRENCY.value}"] = component.currency
        if component.relationship is not FundingRelationship.NOT_STATED:
            displayed[
                f"{prefix}.{MaterialFactKind.FUNDING_RELATIONSHIP.value}"
            ] = component.relationship.value
    for round_entry in record.rounds:
        prefix = subject("round", round_entry.id)
        if round_entry.intake is not None:
            displayed[f"{prefix}.{MaterialFactKind.INTAKE.value}"] = round_entry.intake
        if round_entry.route is not None:
            displayed[
                f"{prefix}.{MaterialFactKind.APPLICATION_ROUTE.value}"
            ] = round_entry.route
    return displayed


def _record_fact_disagreements(record: Opportunity, facts: MaterialFacts) -> list[str]:
    """Whatever the record displays must be what its fact table states."""

    held: list[str] = []
    for key, shown in _displayed_facts(record).items():
        fact = facts.find(key)
        if fact is None:
            continue  # already held as a missing required fact
        if fact.state is not FactState.STATED:
            held.append(
                f"{key}: the record shows {shown!r} but the fact is {fact.state.value}"
            )
        elif not _same_reading(key, shown, fact.value or ""):
            held.append(
                f"{key}: the record shows {shown!r} but the fact states {fact.value!r}"
            )
    return held


def _same_reading(key: str, shown: str, stated: str) -> bool:
    """Compare a displayed value with a fact's value the way each field is read."""

    if key.endswith(f".{MaterialFactKind.AMOUNT.value}"):
        shown_digits = digits_only(shown)
        return bool(shown_digits) and shown_digits == digits_only(stated)
    return normalise(shown.replace("_", " ")) == normalise(stated.replace("_", " "))
