"""Operational contracts for the automated publication gate (D-11, D-12).

These objects are separate from the YAML ``Opportunity`` format on purpose. A
candidate record is a proposal; a ``SourceSnapshot`` is retained source
content; a ``ValidationReport`` is the evidence check over that content; and a
``PublicationDecision`` is what the code gate concluded. Only a decision the
code itself produces can make a record public.

Nothing here can carry human approval: there is no verified-by field and no
assurance level above ``source_checked``.
"""

import hashlib
from datetime import datetime
from enum import StrEnum

from pydantic import Field, HttpUrl, field_validator, model_validator

from app.domain.enums import PublicationAssurance
from app.domain.models import DomainModel, Identifier


class CheckResult(StrEnum):
    """Outcome of checking one claim against its retained snapshot."""

    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNCLEAR = "unclear"


class DecisionType(StrEnum):
    """Publish, hold or reject, as defined by ``PUBLICATION-POLICY.md``."""

    PUBLISH = "publish"
    HOLD = "hold"
    REJECT = "reject"


class SourceSnapshot(DomainModel):
    """Immutable retained source content that excerpts are matched against.

    ``body`` is the extracted text as stored. ``content_hash`` is derived from
    it, so two snapshots can never share an id with different content.
    """

    id: Identifier
    url: HttpUrl
    body: str = Field(
        min_length=1,
        description="Retained page text; every excerpt is matched against it.",
    )
    response_status: int = Field(default=200, ge=100, le=599)
    retrieved_at: datetime
    parser_version: str = Field(min_length=1)

    @field_validator("retrieved_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("snapshot timestamps must include a timezone")
        return value

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.body.encode("utf-8")).hexdigest()


class ClaimCheck(DomainModel):
    """One evidence-check result for one claim in the candidate record.

    ``excerpt`` is the quoted span the checker relied on. The gate re-checks
    that it occurs in the named snapshot, so a checker cannot cite text that
    was not retained.
    """

    claim: str = Field(min_length=1, description="What is being checked, in our words.")
    evidence_id: Identifier
    snapshot_id: Identifier
    excerpt: str = Field(min_length=1)
    result: CheckResult
    reason: str | None = Field(
        default=None,
        description="Why the check returned this result; required when not supported.",
    )

    @model_validator(mode="after")
    def unresolved_results_state_a_reason(self) -> "ClaimCheck":
        if self.result is not CheckResult.SUPPORTED and not self.reason:
            raise ValueError("an unsupported or unclear claim must state a reason")
        return self


class ValidationReport(DomainModel):
    """The evidence check over one exact candidate revision.

    ``content_hash`` pins the report to a revision: a report written for one
    version of the facts cannot publish a different one. ``policy_version``
    pins it to the gate that produced it.
    """

    opportunity_id: Identifier
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_version: str = Field(min_length=1)
    checked_at: datetime
    checks: tuple[ClaimCheck, ...] = Field(min_length=1)

    @field_validator("checked_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("checked_at must include a timezone")
        return value


class PublicationDecision(DomainModel):
    """What the code gate decided, with machine-readable reasons."""

    opportunity_id: Identifier
    decision: DecisionType
    assurance: PublicationAssurance
    policy_version: str = Field(min_length=1)
    checked_at: datetime
    snapshot_ids: tuple[Identifier, ...] = ()
    reasons: tuple[str, ...] = ()

    @model_validator(mode="after")
    def assurance_matches_decision(self) -> "PublicationDecision":
        if self.decision is DecisionType.PUBLISH:
            if self.reasons:
                raise ValueError("a publish decision cannot carry hold reasons")
            if self.assurance is not PublicationAssurance.SOURCE_CHECKED:
                raise ValueError("a publish decision must carry source_checked")
            if not self.snapshot_ids:
                raise ValueError("a publish decision must reference its snapshots")
        else:
            if not self.reasons:
                raise ValueError("a non-publish decision must state a reason")
            if self.assurance is not PublicationAssurance.INSUFFICIENT_EVIDENCE:
                raise ValueError("a non-publish decision cannot claim a source check")
        return self


class PublishedRevision(DomainModel):
    """An immutable published version created by the gate."""

    opportunity_id: Identifier
    revision: int = Field(ge=1)
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    decision: PublicationDecision


__all__ = [
    "CheckResult",
    "ClaimCheck",
    "DecisionType",
    "PublicationDecision",
    "PublishedRevision",
    "SourceSnapshot",
    "ValidationReport",
]
