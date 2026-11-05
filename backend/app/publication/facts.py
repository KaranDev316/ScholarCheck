"""Material facts and their states (T06, CONTEXT rule 5).

A candidate record says what it displays; a material-fact table says what the
source does about each decision-critical field. The state is part of the fact,
so a field the page does not cover is recorded as ``unspecified`` with a reason
rather than hidden behind a bare ``None``, and two pages that disagree are
recorded as ``conflicting`` with both readings kept.

Every reading carries its own field-level evidence: the evidence id, the
snapshot it came from and the exact span quoted. The gate re-checks that span
against the retained snapshot, so a fact cannot be backed by text the page does
not contain.
"""

import hashlib
import json
from enum import StrEnum
from typing import Annotated

from pydantic import Field, StringConstraints, model_validator

from app.domain.models import DomainModel, Identifier, Opportunity

Subject = Annotated[
    str,
    StringConstraints(
        pattern=r"^(record|round|component|rule|programme)(:[a-z0-9]+(?:-[a-z0-9]+)*)?$",
        max_length=120,
    ),
    Field(
        description=(
            "What the fact is about: 'record', or '<kind>:<id>' such as "
            "'component:fund-living'."
        )
    ),
]

FactKey = Annotated[
    str,
    StringConstraints(
        pattern=(
            r"^((record)|((round|component|rule|programme):[a-z0-9]+(?:-[a-z0-9]+)*))"
            r"\.[a-z][a-z_]*$"
        ),
        max_length=140,
    ),
    Field(description="Subject and kind, e.g. 'component:fund-living.amount'."),
]


class FactState(StrEnum):
    """How a material fact stands in the retained sources (CONTEXT rule 5)."""

    STATED = "stated"
    UNSPECIFIED = "unspecified"
    CONFLICTING = "conflicting"


class MaterialFactKind(StrEnum):
    """The fields the policy requires a fact and a passage for (gate 2)."""

    SUMMARY = "summary"
    DESCRIPTION = "description"
    CONDITIONS = "conditions"
    PROGRAMME = "programme"
    LABEL = "label"
    PERIOD = "period"
    COVERAGE = "coverage"
    AMOUNT = "amount"
    CURRENCY = "currency"
    RATE_YEAR = "rate_year"
    DEADLINE = "deadline"
    STAGE = "stage"
    INTAKE = "intake"
    APPLICATION_ROUTE = "application_route"
    ELIGIBILITY_RESTRICTION = "eligibility_restriction"
    FUNDING_RELATIONSHIP = "funding_relationship"


class DeadlineStage(StrEnum):
    """The stage a deadline belongs to (CONTEXT rule 4)."""

    EOI = "eoi"
    ADMISSION = "admission"
    SCHOLARSHIP = "scholarship"
    NOMINATION = "nomination"
    UNIVERSITY = "university"


COMPONENT_FACT_KINDS: tuple[MaterialFactKind, ...] = (
    MaterialFactKind.DESCRIPTION,
    MaterialFactKind.CONDITIONS,
    MaterialFactKind.PERIOD,
    MaterialFactKind.COVERAGE,
    MaterialFactKind.AMOUNT,
    MaterialFactKind.CURRENCY,
    MaterialFactKind.FUNDING_RELATIONSHIP,
    MaterialFactKind.RATE_YEAR,
)

ROUND_FACT_KINDS: tuple[MaterialFactKind, ...] = (
    MaterialFactKind.LABEL,
    MaterialFactKind.INTAKE,
    MaterialFactKind.APPLICATION_ROUTE,
    MaterialFactKind.DEADLINE,
    MaterialFactKind.STAGE,
)


def normalise(text: str) -> str:
    """Compare wording the way the gate compares excerpts: case and spacing only."""

    return " ".join(text.split()).casefold()


def subject(kind: str, identifier: str | None = None) -> str:
    """Build a fact subject, e.g. ``subject("component", "fund-living")``."""

    return kind if identifier is None else f"{kind}:{identifier}"


class FactReading(DomainModel):
    """One thing a source says about a fact, with the span that says it.

    ``value`` is the reading in the page's own terms; a fact whose readings
    disagree is ``conflicting``. Evidence id, snapshot id and excerpt together
    are the field-level evidence the gate re-checks.
    """

    value: str = Field(min_length=1, max_length=4000)
    evidence_id: Identifier
    snapshot_id: Identifier
    excerpt: str = Field(
        min_length=1, description="The exact span that states this reading."
    )


class MaterialFact(DomainModel):
    """One decision-critical field, its state and the evidence behind it.

    A ``stated`` fact carries the value and at least one reading, and every
    reading agrees. An ``unspecified`` fact carries no reading and must say why
    the source does not state it. A ``conflicting`` fact carries the readings
    that disagree and must say what conflicts. Uncertainty is never a bare
    ``None``: the state is the answer.
    """

    kind: MaterialFactKind
    subject: Subject
    state: FactState
    value: str | None = Field(default=None, max_length=4000)
    readings: tuple[FactReading, ...] = ()
    reason: str | None = Field(
        default=None,
        description="Why the fact is unspecified or conflicting, in our words.",
    )

    @model_validator(mode="after")
    def state_matches_its_evidence(self) -> "MaterialFact":
        values = {normalise(reading.value) for reading in self.readings}
        if self.state is FactState.STATED:
            if self.value is None:
                raise ValueError("a stated fact must carry its value")
            if not self.readings:
                raise ValueError("a stated fact must cite at least one reading")
            if len(values) > 1:
                raise ValueError("readings that disagree make the fact conflicting")
            if normalise(self.value) not in values:
                raise ValueError("a stated fact's value must match its readings")
            if self.reason is not None:
                raise ValueError("a stated fact cannot carry an unresolved reason")
            if self.kind is MaterialFactKind.STAGE:
                allowed = {stage.value for stage in DeadlineStage}
                if self.value not in allowed:
                    raise ValueError(
                        "a stated stage must be one of: " + ", ".join(sorted(allowed))
                    )
        elif self.state is FactState.UNSPECIFIED:
            if self.value is not None or self.readings:
                raise ValueError("an unspecified fact cannot carry a value or a reading")
            if not self.reason:
                raise ValueError(
                    "an unspecified fact must say why the source does not state it"
                )
        else:
            if self.value is not None:
                raise ValueError("a conflicting fact cannot publish a single value")
            if len(values) < 2:
                raise ValueError(
                    "a conflicting fact needs at least two readings that disagree"
                )
            if not self.reason:
                raise ValueError("a conflicting fact must say what conflicts")
        return self

    @property
    def key(self) -> str:
        """The field this fact records, e.g. ``component:fund-living.amount``."""

        return f"{self.subject}.{self.kind.value}"

    @property
    def evidence_refs(self) -> tuple[str, ...]:
        """The evidence entries this fact reads from, in order, without repeats."""

        return tuple(dict.fromkeys(reading.evidence_id for reading in self.readings))

    @property
    def excerpts(self) -> tuple[str, ...]:
        """The exact spans this fact is backed by."""

        return tuple(dict.fromkeys(reading.excerpt for reading in self.readings))


class MaterialFacts(DomainModel):
    """Every material fact recorded for one candidate revision."""

    facts: tuple[MaterialFact, ...] = ()

    @model_validator(mode="after")
    def one_fact_per_field(self) -> "MaterialFacts":
        keys = [fact.key for fact in self.facts]
        repeated = sorted({key for key in keys if keys.count(key) > 1})
        if repeated:
            raise ValueError("one fact per field; repeated: " + ", ".join(repeated))
        return self

    def find(self, key: str) -> MaterialFact | None:
        """The fact recorded for ``key``, or None when the field was not recorded."""

        return next((fact for fact in self.facts if fact.key == key), None)

    @property
    def keys(self) -> tuple[str, ...]:
        return tuple(fact.key for fact in self.facts)

    @property
    def stated(self) -> tuple[MaterialFact, ...]:
        return tuple(fact for fact in self.facts if fact.state is FactState.STATED)

    @property
    def unspecified(self) -> tuple[MaterialFact, ...]:
        return tuple(fact for fact in self.facts if fact.state is FactState.UNSPECIFIED)

    @property
    def conflicting(self) -> tuple[MaterialFact, ...]:
        return tuple(fact for fact in self.facts if fact.state is FactState.CONFLICTING)

    @property
    def fingerprint(self) -> str:
        """Stable hash of the table, so a report can be tied to what it checked."""

        payload = [
            fact.model_dump(mode="json", by_alias=False)
            for fact in sorted(self.facts, key=lambda fact: fact.key)
        ]
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()


def required_fact_keys(record: Opportunity) -> tuple[str, ...]:
    """Every fact the record itself obliges a candidate to record.

    A recorded amount, currency, relationship, intake or route is a displayed
    claim, so each needs a fact. The fields the record cannot display — rate
    year, deadline, stage — are required too: the extraction pass has to say
    what the source does about them instead of dropping what it read.
    """

    keys: list[str] = ["record.summary"]
    keys.extend(f"programme:{p.id}.programme" for p in record.programmes)
    for component in record.funding_components:
        keys.extend(
            f"{subject('component', component.id)}.{kind.value}"
            for kind in COMPONENT_FACT_KINDS
        )
    for round_entry in record.rounds:
        keys.extend(
            f"{subject('round', round_entry.id)}.{kind.value}"
            for kind in ROUND_FACT_KINDS
        )
    for rule in record.eligibility_rules:
        keys.append(
            f"{subject('rule', rule.id)}.{MaterialFactKind.ELIGIBILITY_RESTRICTION.value}"
        )
    return tuple(keys)


__all__ = [
    "COMPONENT_FACT_KINDS",
    "DeadlineStage",
    "FactKey",
    "FactReading",
    "FactState",
    "MaterialFact",
    "MaterialFactKind",
    "MaterialFacts",
    "ROUND_FACT_KINDS",
    "Subject",
    "normalise",
    "required_fact_keys",
    "subject",
]


def programme_value(programme) -> str:
    """Canonical displayed programme claims checked as a single structured field."""
    return programme.model_dump_json(exclude={"id"})
