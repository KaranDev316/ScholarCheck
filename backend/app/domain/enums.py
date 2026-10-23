"""Shared domain enumerations (S01 T02).

These values are the wire format. They appear verbatim in API responses, so
members must stay stable and ``lower_snake_case``. Adding a member is a
contract change: update ``frontend/src/types/domain.ts`` in the same step.

Domain rules referenced here live in ``docs/CONTEXT.md`` section 5.
"""

from enum import StrEnum


class AssessmentOutcome(StrEnum):
    """The four permitted overall outcomes (CONTEXT rule 1).

    There is no percentage, score or probability member by design.
    """

    MEETS_CHECKED_REQUIREMENTS = "meets_checked_requirements"
    POTENTIAL_FIT_CONFIRMATION_NEEDED = "potential_fit_confirmation_needed"
    DOES_NOT_MEET_STATED_REQUIREMENT = "does_not_meet_stated_requirement"
    INSUFFICIENT_INFORMATION = "insufficient_information"


class RuleResult(StrEnum):
    """Per-rule result.

    ``UNRESOLVED`` is used when the published requirement cannot be settled
    from the stated data (for example an unrecognised three-year degree). It
    can never be treated as satisfied (CONTEXT rule 6, invariant 1).
    """

    MET = "met"
    NOT_MET = "not_met"
    UNRESOLVED = "unresolved"
    INSUFFICIENT_INFORMATION = "insufficient_information"


class EligibilityRuleKind(StrEnum):
    """What a single eligibility rule tests against the profile."""

    NATIONALITY = "nationality"
    RESIDENCE = "residence"
    DEGREE_LEVEL = "degree_level"
    DEGREE_TYPE = "degree_type"
    DEGREE_DURATION = "degree_duration"
    DEGREE_STATUS = "degree_status"
    GRADE = "grade"
    INSTITUTION_RECOGNITION = "institution_recognition"
    ENROLMENT_STATUS = "enrolment_status"
    OTHER = "other"


class DegreeLevel(StrEnum):
    """Level of a programme, or of the applicant's intended study.

    Bachelor's, master's (taught or research) and doctoral study are all in
    scope (CONTEXT D-08). Levels stay distinct: a rule that names one level is
    never satisfied by another.
    """

    BACHELOR = "bachelor"
    TAUGHT_MASTER = "taught_master"
    RESEARCH_MASTER = "research_master"
    DOCTORAL = "doctoral"


class DegreeStatus(StrEnum):
    """Status of the qualification the applicant holds or is completing."""

    ONGOING = "ongoing"
    COMPLETED = "completed"


class FundingComponentKind(StrEnum):
    """Funding is shown per component and never summed (CONTEXT rule 3)."""

    TUITION = "tuition"
    LIVING_SUPPORT = "living_support"
    ACCOMMODATION = "accommodation"
    INSURANCE = "insurance"
    TRAVEL = "travel"
    UPFRONT_COST = "upfront_cost"
    OTHER = "other"


class FundingStatus(StrEnum):
    """How completely a funding component is described by the source.

    ``UNSPECIFIED`` exists so missing information is never shown as zero or as
    full coverage (CONTEXT rule 3, invariant 2).
    """

    SPECIFIED = "specified"
    PARTIAL = "partial"
    UNSPECIFIED = "unspecified"


class FundingRelationship(StrEnum):
    """What kind of money the component is.

    A tuition waiver and a stipend are different relationships between the
    funder and the student; they are never interchangeable (CONTEXT rule 3).
    """

    TUITION_REDUCTION = "tuition_reduction"
    GRANT = "grant"
    LOAN = "loan"
    EMPLOYMENT = "employment"
    NOT_STATED = "not_stated"
