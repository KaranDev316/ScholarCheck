"""Read response for a fixture or future published opportunity."""

from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import Field, field_validator, model_validator

from app.domain.models import DomainModel, Opportunity


class PublicationAssurance(StrEnum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    SOURCE_CHECKED = "source_checked"
    HUMAN_VERIFIED = "human_verified"


class Freshness(StrEnum):
    NOT_CHECKED = "not_checked"
    CURRENT = "current"
    NEEDS_RECHECK = "needs_recheck"
    STALE = "stale"


class PublicationMetadata(DomainModel):
    assurance: PublicationAssurance
    source_checked_at: datetime | None = None
    validation_policy_version: str | None = None
    freshness: Freshness

    @field_validator("source_checked_at")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("source_checked_at must include a timezone")
        return value

    @model_validator(mode="after")
    def checked_metadata_matches_assurance(self) -> Self:
        checked = self.assurance is not PublicationAssurance.INSUFFICIENT_EVIDENCE
        has_time = self.source_checked_at is not None
        has_policy = self.validation_policy_version is not None
        if has_time != checked or has_policy != checked:
            raise ValueError("source check time and policy version must match assurance")
        return self


class OpportunityResponse(DomainModel):
    opportunity: Opportunity
    publication: PublicationMetadata
    is_published: bool = Field(
        description="False for development fixture previews; publication begins in S04."
    )
