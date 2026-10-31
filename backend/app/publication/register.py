"""The review findings that hold a candidate until they are resolved.

``content/publication/first-pass-review.json`` is the machine-readable form of
the first-pass review. The gate never takes these findings from whoever is
publishing: ``store.publish`` loads the register itself, so no code path can
decide that a recorded discrepancy does not apply, and dropping the argument is
not possible. A register that cannot be read holds every candidate instead of
reading as "nothing outstanding".

A finding holds any record that carries the evidence entry it names *or* that
cites the page it was raised on, so renaming a record cannot launder a claim the
review already doubted.

Removing an entry is a reviewed change: it should only follow a corrected
fixture re-checked against a retained snapshot, not a new validation report that
claims support.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.domain.models import Identifier, Opportunity
from app.publication.contracts import CheckResult

REGISTER_PATH = (
    Path(__file__).resolve().parents[3]
    / "content"
    / "publication"
    / "first-pass-review.json"
)


class Finding(BaseModel):
    """One unresolved discrepancy raised against a record and one of its pages."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    evidence_id: Identifier
    evidence_url: HttpUrl = Field(
        description="The page the finding was raised on, held with the claim.",
    )
    result: CheckResult
    reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def must_be_unresolved(self) -> "Finding":
        if self.result is CheckResult.SUPPORTED:
            raise ValueError("a recorded finding must be unsupported or unclear")
        return self


class RegisterPayload(BaseModel):
    """The register file as written, validated so it cannot be misread."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    reviewed_at: date
    source: str = Field(min_length=1)
    note: str = Field(min_length=1)
    findings: dict[Identifier, tuple[Finding, ...]]


@dataclass(frozen=True)
class FindingsRegister:
    """Recorded findings, or the reason none could be read."""

    entries: dict[str, tuple[Finding, ...]] = field(default_factory=dict)
    problem: str | None = None

    @property
    def readable(self) -> bool:
        return self.problem is None

    def holds(self, record: Opportunity) -> tuple[str, ...]:
        """The reasons this record must stay held; empty when none apply."""

        if self.problem is not None:
            return (
                "the review findings register could not be read "
                f"({self.problem}), so unresolved findings cannot be ruled out",
            )

        pages = {str(entry.url) for entry in record.evidence}
        reasons: list[str] = []
        for opportunity_id, findings in self.entries.items():
            for finding in findings:
                page_under_review = str(finding.evidence_url) in pages
                if opportunity_id != record.id and not page_under_review:
                    continue
                reason = " ".join(finding.reason.split())
                reasons.append(f"{finding.evidence_id}: open review finding: {reason}")
        return tuple(reasons)


def load_register(path: Path | None = None) -> FindingsRegister:
    """Read the findings register, or hold everything if it cannot be read."""

    target = REGISTER_PATH if path is None else path
    try:
        payload = RegisterPayload.model_validate(
            json.loads(target.read_text(encoding="utf-8"))
        )
    except (OSError, ValueError) as error:
        detail = str(error).splitlines()[0][:200]
        return FindingsRegister(problem=f"{target.name}: {detail}")

    return FindingsRegister(
        entries={key: tuple(value) for key, value in payload.findings.items()}
    )


__all__ = ["Finding", "FindingsRegister", "REGISTER_PATH", "load_register"]
