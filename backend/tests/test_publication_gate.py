"""S01 F-08: publication needs a report the code gate can verify.

Every case here is pure: no database, no network. The gate must decide from the
candidate, the validation report, the retained snapshots and the review findings
register alone.
"""

import inspect
from datetime import timedelta

from app.domain.enums import DegreeLevel, PublicationAssurance
from app.domain.models import Evidence, Opportunity
from app.publication.contracts import (
    Applicability,
    CheckResult,
    ClaimCheck,
    DecisionType,
    ValidationReport,
)
from app.publication.facts import (
    FactState,
    MaterialFact,
    MaterialFacts,
    MaterialFactKind,
    required_fact_keys,
)
from app.publication.gates import evaluate
from app.publication.register import FindingsRegister
from app.storage.opportunities import CONTENT_DIR, read_seed
from tests.publication_helpers import (
    RETRIEVED_AT,
    SAMPLE_PASSAGE as PASSAGE,
    SAMPLE_URL as URL,
    build_report,
    build_snapshots,
    held_register,
    no_findings,
    sample_record as record,
)


def decide(
    candidate: Opportunity,
    *,
    snapshots=None,
    report=None,
    register: FindingsRegister | None = None,
    gate_kwargs: dict | None = None,
    **report_kwargs,
):
    """Run the gate with snapshots and a report built from the record."""

    retained = snapshots if snapshots is not None else build_snapshots(candidate)
    checked = (
        report
        if report is not None
        else build_report(candidate, retained, **report_kwargs)
    )
    return evaluate(
        candidate,
        checked,
        {snapshot.id: snapshot for snapshot in retained},
        register=no_findings() if register is None else register,
        **(gate_kwargs or {}),
    )


def with_facts(
    report: ValidationReport, facts: tuple[MaterialFact, ...]
) -> ValidationReport:
    """The same report with its fact table rewritten, as a bad checker might."""

    return report.model_copy(update={"facts": MaterialFacts(facts=facts)})


def with_checks(
    report: ValidationReport, checks: tuple[ClaimCheck, ...]
) -> ValidationReport:
    """The same report with its verdicts rewritten, as a bad checker might."""

    return report.model_copy(update={"checks": checks})


AMOUNT_KEY = f"component:fund-living.{MaterialFactKind.AMOUNT.value}"
RATE_YEAR_KEY = f"component:fund-living.{MaterialFactKind.RATE_YEAR.value}"


def test_a_supported_candidate_is_published_with_its_snapshots() -> None:
    candidate = record()
    snapshots = build_snapshots(candidate)

    decision = decide(candidate, snapshots=snapshots)

    assert decision.decision is DecisionType.PUBLISH
    assert decision.assurance is PublicationAssurance.SOURCE_CHECKED
    assert decision.reasons == ()
    assert decision.snapshot_ids == tuple(sorted(snapshot.id for snapshot in snapshots))


def test_an_unsupported_claim_holds_the_candidate() -> None:
    decision = decide(
        record(),
        results={"ev-value": CheckResult.UNSUPPORTED},
        reasons={"ev-value": "the page states a different amount"},
    )

    assert decision.decision is DecisionType.HOLD
    assert decision.assurance is PublicationAssurance.INSUFFICIENT_EVIDENCE
    assert any(
        "ev-value" in reason and "unsupported" in reason for reason in decision.reasons
    )


def test_an_unclear_claim_holds_the_candidate() -> None:
    decision = decide(
        record(),
        results={"ev-value": CheckResult.UNCLEAR},
        reasons={"ev-value": "the amount is not attributed to this scheme"},
    )

    assert decision.decision is DecisionType.HOLD
    assert any("unclear" in reason for reason in decision.reasons)


def test_an_excerpt_outside_the_snapshot_holds_the_candidate() -> None:
    decision = decide(record(), excerpts={"ev-value": "$50,000 per year"})

    assert decision.decision is DecisionType.HOLD
    assert any("not in the retained snapshot" in reason for reason in decision.reasons)


def test_a_claim_without_a_retained_snapshot_holds_the_candidate() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    orphan = report.checks[0].model_copy(update={"snapshot_id": "snap-missing-page"})
    report = report.model_copy(update={"checks": (orphan,)})

    decision = decide(candidate, snapshots=retained, report=report)

    assert decision.decision is DecisionType.HOLD
    assert any("was not retained" in reason for reason in decision.reasons)


def test_an_unchecked_evidence_entry_holds_the_candidate() -> None:
    candidate = record(
        evidence=(
            Evidence(
                id="ev-value",
                url=URL,
                passage=PASSAGE,
                retrieved_at=RETRIEVED_AT,
            ),
            Evidence(
                id="ev-deadline",
                url=f"{URL}#deadline",
                passage="Directly to the agency: October 17",
                retrieved_at=RETRIEVED_AT,
            ),
        )
    )
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    report = report.model_copy(update={"checks": report.checks[:1]})

    decision = decide(candidate, snapshots=retained, report=report)

    assert decision.decision is DecisionType.HOLD
    assert any("no evidence check covers" in reason for reason in decision.reasons)


def test_two_excerpts_for_one_claim_hold_the_candidate() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    first = report.checks[0]
    second = first.model_copy(update={"excerpt": PASSAGE[:24]})
    report = report.model_copy(update={"checks": (first, second)})

    decision = decide(candidate, snapshots=retained, report=report)

    assert decision.decision is DecisionType.HOLD
    assert any("two different excerpts" in reason for reason in decision.reasons)


def test_an_amount_absent_from_its_passage_holds_the_candidate() -> None:
    candidate = record(
        evidence=(
            Evidence(
                id="ev-value",
                url=URL,
                passage="The scholarship pays an annual stipend for 36 months.",
                retrieved_at=RETRIEVED_AT,
            ),
        )
    )

    decision = decide(candidate)

    assert decision.decision is DecisionType.HOLD
    assert any("is not stated" in reason for reason in decision.reasons)


def test_a_snapshot_from_an_unapproved_provider_is_rejected() -> None:
    decision = decide(record(), gate_kwargs={"approved_hosts": ("example.edu",)})

    assert decision.decision is DecisionType.REJECT
    assert any("not an approved provider" in reason for reason in decision.reasons)


def test_a_report_for_another_revision_is_rejected() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    report = report.model_copy(update={"content_hash": "0" * 64})

    decision = decide(candidate, snapshots=retained, report=report)

    assert decision.decision is DecisionType.REJECT
    assert any("different revision" in reason for reason in decision.reasons)


def test_a_report_from_another_policy_version_is_held() -> None:
    decision = decide(record(), policy_version="s01.publication.0")

    assert decision.decision is DecisionType.HOLD
    assert any("the gate runs" in reason for reason in decision.reasons)


def test_a_snapshot_fetched_at_another_time_is_held() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    stale = retained[0].model_copy(
        update={"retrieved_at": RETRIEVED_AT - timedelta(days=1)}
    )

    decision = decide(candidate, snapshots=(stale,))

    assert decision.decision is DecisionType.HOLD
    assert any("retrieved at a different time" in reason for reason in decision.reasons)


def test_a_citation_and_snapshot_from_different_pages_are_held() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    elsewhere = retained[0].model_copy(update={"url": f"{URL}#other"})

    decision = decide(candidate, snapshots=(elsewhere,), report=report)

    assert decision.decision is DecisionType.HOLD
    assert any("different pages" in reason for reason in decision.reasons)


def test_the_gate_cannot_be_asked_to_decide_without_the_register() -> None:
    """A default would let a caller publish a held record by saying nothing."""

    parameter = inspect.signature(evaluate).parameters["register"]

    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY


def test_a_recorded_finding_holds_a_fully_supporting_report() -> None:
    findings = held_register(
        "gate-sample", "ev-value", URL, "the page states a different amount"
    )

    decision = decide(record(), register=findings)

    assert decision.decision is DecisionType.HOLD
    assert any(
        "ev-value" in reason and "the page states a different amount" in reason
        for reason in decision.reasons
    )


def test_a_finding_holds_any_record_citing_the_page_it_was_raised_on() -> None:
    """A new id must not launder a claim the review already doubted."""

    other_id = "gate-sample-copy"
    findings = held_register(
        "some-other-record", "ev-value", URL, "the amount is unconfirmed"
    )
    candidate = record().model_copy(update={"id": other_id})
    snapshots = build_snapshots(candidate)

    decision = decide(candidate, snapshots=snapshots, register=findings)

    assert decision.decision is DecisionType.HOLD
    assert any("the amount is unconfirmed" in reason for reason in decision.reasons)


def test_a_register_that_cannot_be_read_holds_the_candidate() -> None:
    unreadable = FindingsRegister(problem="first-pass-review.json: not found")

    decision = decide(record(), register=unreadable)

    assert decision.decision is DecisionType.HOLD
    assert any("could not be read" in reason for reason in decision.reasons)


def test_a_field_with_no_material_fact_holds_the_candidate() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    kept = tuple(fact for fact in report.facts.facts if fact.key != AMOUNT_KEY)

    decision = decide(
        candidate, snapshots=retained, report=with_facts(report, kept)
    )

    assert decision.decision is DecisionType.HOLD
    assert any(
        f"{AMOUNT_KEY}: the candidate records no material fact" in reason
        for reason in decision.reasons
    )


def test_a_fact_the_record_contradicts_holds_the_candidate() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    amount = report.facts.find(AMOUNT_KEY)
    assert amount is not None
    reading = amount.readings[0].model_copy(update={"value": "50000"})
    changed = amount.model_copy(update={"value": "50000", "readings": (reading,)})
    facts = tuple(
        changed if fact.key == AMOUNT_KEY else fact for fact in report.facts.facts
    )

    decision = decide(candidate, snapshots=retained, report=with_facts(report, facts))

    assert decision.decision is DecisionType.HOLD
    assert any(
        "the record shows '40000' but the fact states '50000'" in reason
        for reason in decision.reasons
    )


def test_a_fact_span_no_supported_check_quotes_holds_the_candidate() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    entry_checks = tuple(
        check for check in report.checks if check.fact is None
    )

    decision = decide(
        candidate, snapshots=retained, report=with_checks(report, entry_checks)
    )

    assert decision.decision is DecisionType.HOLD
    assert any(
        "no supported check quotes the span" in reason
        for reason in decision.reasons
    )


def test_a_verdict_about_an_unspecified_fact_holds_the_candidate() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    extra = ClaimCheck(
        claim="rate year for component:fund-living",
        evidence_id="ev-value",
        snapshot_id=retained[0].id,
        excerpt=PASSAGE,
        result=CheckResult.SUPPORTED,
        fact=RATE_YEAR_KEY,
        applies_to=Applicability(note="the page states the rate year"),
    )

    decision = decide(
        candidate,
        snapshots=retained,
        report=with_checks(report, (*report.checks, extra)),
    )

    assert decision.decision is DecisionType.HOLD
    assert any("has no claim to support" in reason for reason in decision.reasons)


def test_a_verdict_quoting_text_the_fact_does_not_carry_holds_the_candidate() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    shortened = tuple(
        check.model_copy(update={"excerpt": PASSAGE[:24]})
        if check.fact == AMOUNT_KEY
        else check
        for check in report.checks
    )

    decision = decide(
        candidate, snapshots=retained, report=with_checks(report, shortened)
    )

    assert decision.decision is DecisionType.HOLD
    assert any(
        "quotes a span this fact does not carry" in reason
        for reason in decision.reasons
    )


def test_a_fact_read_from_evidence_off_the_record_is_rejected() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    amount = report.facts.find(AMOUNT_KEY)
    assert amount is not None
    ghost = amount.readings[0].model_copy(update={"evidence_id": "ev-ghost"})
    changed = amount.model_copy(update={"readings": (ghost,)})
    facts = tuple(
        changed if fact.key == AMOUNT_KEY else fact for fact in report.facts.facts
    )

    decision = decide(candidate, snapshots=retained, report=with_facts(report, facts))

    assert decision.decision is DecisionType.REJECT
    assert any(
        "reads from evidence that is not on the record" in reason
        for reason in decision.reasons
    )


def test_a_fact_about_a_part_the_record_lacks_is_rejected() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    ghost = MaterialFact(
        kind=MaterialFactKind.CURRENCY,
        subject="component:ghost",
        state=FactState.UNSPECIFIED,
        reason="the record has no such component",
    )

    decision = decide(
        candidate,
        snapshots=retained,
        report=with_facts(report, (*report.facts.facts, ghost)),
    )

    assert decision.decision is DecisionType.REJECT
    assert any(
        "the record has no component:ghost to state a fact about" in reason
        for reason in decision.reasons
    )


def test_a_fact_reading_a_span_its_page_lacks_is_held() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    amount = report.facts.find(AMOUNT_KEY)
    assert amount is not None
    elsewhere = amount.readings[0].model_copy(
        update={"excerpt": "The scholarship pays $50,000 a year."}
    )
    changed = amount.model_copy(update={"readings": (elsewhere,)})
    facts = tuple(
        changed if fact.key == AMOUNT_KEY else fact for fact in report.facts.facts
    )

    decision = decide(candidate, snapshots=retained, report=with_facts(report, facts))

    assert decision.decision is DecisionType.HOLD
    assert any(
        "the quoted span is not in the retained snapshot" in reason
        for reason in decision.reasons
    )


def test_two_claims_on_one_page_may_quote_different_spans() -> None:
    """Spans are compared per claim, so a shorter quote is not a second excerpt."""

    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    shortened = tuple(
        check.model_copy(update={"excerpt": PASSAGE[:24]})
        if check.fact is None
        else check
        for check in report.checks
    )

    decision = decide(
        candidate, snapshots=retained, report=with_checks(report, shortened)
    )

    assert decision.decision is DecisionType.PUBLISH


def test_a_verdict_placed_in_a_round_the_record_lacks_holds_the_candidate() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    misplaced = tuple(
        check.model_copy(
            update={
                "applies_to": Applicability(
                    rounds=("round-ghost",), note="the quote governs this round"
                )
            }
        )
        if check.fact == AMOUNT_KEY
        else check
        for check in report.checks
    )

    decision = decide(
        candidate, snapshots=retained, report=with_checks(report, misplaced)
    )

    assert decision.decision is DecisionType.HOLD
    assert any(
        "which the record does not have" in reason for reason in decision.reasons
    )


def test_a_verdict_at_a_degree_level_the_record_lacks_holds_the_candidate() -> None:
    candidate = record()
    retained = build_snapshots(candidate)
    report = build_report(candidate, retained)
    misplaced = tuple(
        check.model_copy(
            update={
                "applies_to": Applicability(
                    degree_level=DegreeLevel.DOCTORAL,
                    note="the quote governs doctoral study",
                )
            }
        )
        if check.fact == AMOUNT_KEY
        else check
        for check in report.checks
    )

    decision = decide(
        candidate, snapshots=retained, report=with_checks(report, misplaced)
    )

    assert decision.decision is DecisionType.HOLD
    assert any(
        "which the record does not offer" in reason for reason in decision.reasons
    )


def test_every_seed_fixture_carries_a_fact_for_every_obliged_field() -> None:
    """The launch fixtures can pass the gate: their holds come from findings.

    RMIT holds in production because the register names it, not because its fact
    table is incomplete, so every fixture must reach `publish` against a
    supporting report and an empty register.
    """

    for path in sorted(CONTENT_DIR.glob("*.yaml")):
        candidate = read_seed(path)
        retained = build_snapshots(candidate)
        report = build_report(candidate, retained)
        missing = [
            key
            for key in required_fact_keys(candidate)
            if report.facts.find(key) is None
        ]

        decision = decide(candidate, snapshots=retained, report=report)

        assert missing == [], f"{path.name} states no fact for {missing}"
        assert decision.decision is DecisionType.HOLD, path.name  # synthetic endorsements cannot prove qualifiers
