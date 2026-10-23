"""Domain models (S01 T02).

Entity boundaries follow ``docs/CONTEXT.md`` section 4: Opportunity (stable
scheme), Round (intake/year/route, identity only until S02), Programme (funded
degree), EligibilityRule, FundingComponent, Evidence.

All models are frozen and reject unknown fields: catalogue content is read-only
reference data, so a typo in a seed file must fail loudly rather than silently
disappear. JSON is emitted in ``camelCase`` (``alias_generator``) so the
TypeScript client keeps its ``camelCase`` convention while Python stays
``snake_case``.
"""

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StringConstraints,
    ValidationInfo,
    field_validator,
)
from pydantic.alias_generators import to_camel

from app.domain.enums import (
    AssessmentOutcome,
    DegreeLevel,
    DegreeStatus,
    EligibilityRuleKind,
    FundingComponentKind,
    FundingRelationship,
    FundingStatus,
    RuleResult,
)

CountryCode = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Z]{2}$"),
    Field(description="ISO 3166-1 alpha-2 country code, upper case (e.g. 'MW')."),
]

CurrencyCode = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Z]{3}$"),
    Field(description="ISO 4217 currency code, upper case (e.g. 'CAD')."),
]

Identifier = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        min_length=3,
        max_length=80,
    ),
    Field(description="Stable lower-case slug used as a public identifier."),
]


class DomainModel(BaseModel):
    """Base for domain models: immutable, no unknown fields, camelCase JSON."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )


class Evidence(DomainModel):
    """A checkable source for a decision-critical claim (CONTEXT rule 5).

    ``retrieved_at`` (when the page was fetched) and ``verified_at`` (when a
    human confirmed the passage) are deliberately separate fields. Nothing here
    sets ``verified_at`` automatically: an automatic refresh only ever updates
    ``retrieved_at``.
    """

    id: Identifier
    url: HttpUrl
    passage: str = Field(
        min_length=1,
        description="The supporting text taken from the source.",
    )
    retrieved_at: datetime
    verified_at: datetime | None = None
    verified_by: str | None = Field(
        default=None,
        description="Name or handle of the human who verified the claim.",
    )

    @field_validator("retrieved_at", "verified_at")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("timestamps must include a timezone")
        return value

    @field_validator("verified_at")
    @classmethod
    def verified_cannot_precede_retrieved(
        cls, value: datetime | None, info: ValidationInfo
    ) -> datetime | None:
        retrieved_at = info.data.get("retrieved_at")
        if value is not None and retrieved_at is not None and value < retrieved_at:
            raise ValueError("verified_at cannot be earlier than retrieved_at")
        return value


class Programme(DomainModel):
    """A specific funded degree offered by an institution."""

    id: Identifier
    name: str = Field(min_length=1)
    degree_level: DegreeLevel
    institution: str = Field(min_length=1)
    country: CountryCode
    duration_years: float | None = Field(
        default=None,
        gt=0,
        le=10,
        description="Published nominal duration, or None when not stated.",
    )
    research_component: bool | None = Field(
        default=None,
        description="None when the source does not say whether research is required.",
    )


class Round(DomainModel):
    """One intake/route of an opportunity. Identity only until S02."""

    id: Identifier
    label: str = Field(min_length=1, description="Human label, e.g. '2027 entry'.")
    intake: str | None = Field(
        default=None,
        description="Intake as written by the funder, e.g. 'September 2027'.",
    )
    route: str | None = Field(
        default=None,
        description="Application route this round belongs to, e.g. 'nomination'.",
    )


class EligibilityRule(DomainModel):
    """One stated requirement, assessed on its own.

    ``blocking`` marks a condition that excludes an applicant outright when it
    is not met. An empty ``evidence_refs`` means the rule is unverified and can
    never produce a "meets" result (CONTEXT rule 5, invariant 1).
    """

    id: Identifier
    requirement: str = Field(
        min_length=1,
        description="The requirement restated in our own words.",
    )
    kind: EligibilityRuleKind
    blocking: bool = False
    evidence_refs: tuple[Identifier, ...] = Field(default=())


class FundingComponent(DomainModel):
    """A single funding element, e.g. a tuition reduction or living support.

    There is intentionally no total field and no sum helper: components are
    never added into a "you receive" figure (CONTEXT rule 3).
    """

    id: Identifier
    kind: FundingComponentKind
    status: FundingStatus
    relationship: FundingRelationship = FundingRelationship.NOT_STATED
    description: str | None = Field(
        default=None,
        description="What the source says this component covers, in our own words.",
    )
    amount: Decimal | None = Field(
        default=None,
        ge=0,
        description="Value exactly as published; None when unspecified.",
    )
    currency: CurrencyCode | None = None
    period: str | None = Field(
        default=None,
        description="Period as published, e.g. 'per year' or 'one-off'.",
    )
    conditions: tuple[str, ...] = Field(
        default=(),
        description="Ongoing conditions, e.g. 'renewed annually subject to progress'.",
    )
    evidence_refs: tuple[Identifier, ...] = Field(default=())

    @field_validator("amount")
    @classmethod
    def amount_requires_specified_status(
        cls, value: Decimal | None, info: ValidationInfo
    ) -> Decimal | None:
        if value is not None and info.data.get("status") is FundingStatus.UNSPECIFIED:
            raise ValueError("an unspecified component cannot carry an amount")
        return value

    @field_validator("currency")
    @classmethod
    def currency_requires_amount(
        cls, value: str | None, info: ValidationInfo
    ) -> str | None:
        if value is not None and info.data.get("amount") is None:
            raise ValueError("currency without an amount would imply a value")
        return value


class OfficialLinks(DomainModel):
    """The three distinct actions a listing offers (AC-04)."""

    summary_url: HttpUrl
    requirements_url: HttpUrl
    portal_url: HttpUrl


class Opportunity(DomainModel):
    """A stable scheme: the thing a student decides whether to pursue."""

    id: Identifier
    scheme_name: str = Field(min_length=1)
    funder: str = Field(min_length=1)
    destinations: tuple[CountryCode, ...] = Field(min_length=1)
    summary: str = Field(
        min_length=1,
        description="Our own short description. Never a copy of source text.",
    )
    links: OfficialLinks
    programmes: tuple[Programme, ...] = ()
    rounds: tuple[Round, ...] = ()
    eligibility_rules: tuple[EligibilityRule, ...] = ()
    funding_components: tuple[FundingComponent, ...] = ()
    evidence: tuple[Evidence, ...] = ()
    last_retrieved_at: datetime | None = Field(
        default=None,
        description="Most recent automatic fetch of any source. Not a verification.",
    )
    last_verified_at: datetime | None = Field(
        default=None,
        description="Most recent human verification of any claim on this record.",
    )


class Grade(DomainModel):
    """A grade kept exactly as entered (CONTEXT rule 6).

    ``value`` is a string on purpose: no parsing, no conversion, no universal
    scale.
    """

    value: str = Field(min_length=1, max_length=32)
    scale: str = Field(min_length=1, max_length=64)


class Profile(DomainModel):
    """The applicant's stated situation. Evaluated statelessly (D-04)."""

    nationality: CountryCode
    residence_country: CountryCode
    degree_type: str = Field(
        min_length=1,
        max_length=120,
        description="Qualification name as the applicant states it, e.g. 'BCA'.",
    )
    degree_duration_years: int = Field(ge=1, le=12)
    degree_status: DegreeStatus
    intended_level: DegreeLevel
    grade: Grade | None = None


class RuleAssessment(DomainModel):
    """The result of one rule against one profile, with its reason."""

    rule_id: Identifier
    result: RuleResult
    reason: str = Field(min_length=1)
    evidence_refs: tuple[Identifier, ...] = ()


class AssessmentResult(DomainModel):
    """Overall eligibility outcome plus the per-rule reasoning behind it.

    Funding suitability, application availability and competitiveness are
    separate assessments (CONTEXT rule 2) and are not part of this object.
    """

    opportunity_id: Identifier
    round_id: Identifier | None = None
    outcome: AssessmentOutcome
    outcome_reason: str = Field(min_length=1)
    rules: tuple[RuleAssessment, ...] = ()


__all__ = [
    "AssessmentResult",
    "CountryCode",
    "CurrencyCode",
    "DomainModel",
    "EligibilityRule",
    "Evidence",
    "FundingComponent",
    "Grade",
    "Identifier",
    "OfficialLinks",
    "Opportunity",
    "Profile",
    "Programme",
    "Round",
    "RuleAssessment",
]
