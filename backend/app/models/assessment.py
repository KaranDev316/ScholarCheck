"""PROPOSED API contracts pending the T02/T07 gate.

Nothing in this module is routed yet; the assessment endpoint is T07. The
shapes are declared and tested here so the gate can approve one version rather
than two. They are recorded as *proposals* only, not appended to
``docs/slices/S01/VERIFICATION.md`` section 5 until approved.
"""

from app.domain.models import AssessmentResult, DomainModel, Identifier, Profile


class AssessmentRequest(DomainModel):
    """Body of ``POST /api/v1/opportunities/{opportunity_id}/assessment``.

    The profile is sent per request and never stored (D-04, invariant 8).
    ``round_id`` is optional because most fixtures have a single round; when a
    scheme has several routes the caller must name one.
    """

    profile: Profile
    round_id: Identifier | None = None


class AssessmentResponse(DomainModel):
    """200 body. Wraps the result so later phases can add fields additively."""

    assessment: AssessmentResult


__all__ = ["AssessmentRequest", "AssessmentResponse"]
