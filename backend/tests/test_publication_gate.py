"""S01 F-08: publication needs a report the code gate can verify.

Every case here is pure: no database, no network. The gate must decide from the
candidate, the validation report, the retained snapshots and the review findings
register alone.
"""

import inspect
from datetime import timedelta

from app.domain.enums import PublicationAssurance
from app.domain.models import Evidence, Opportunity
from app.publication.contracts import CheckResult, DecisionType
from app.publication.gates import evaluate
from app.publication.register import FindingsRegister
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
            Evidence(id="ev-value", url=URL, passage=PASSAGE, retrieved_at=RETRIEVED_AT),
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
