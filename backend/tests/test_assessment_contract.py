"""T02/T07 proposal: the shape of an assessment exchange and its failures.

These tests pin the *proposal* that the T02/T07 gate approves. They do not
exercise a route; the assessment endpoint lands in T07.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.errors import ErrorBody, ErrorCode, FieldError
from app.domain.enums import AssessmentOutcome
from app.domain.models import AssessmentResult, Profile, RuleAssessment
from app.models.assessment import AssessmentRequest, AssessmentResponse


def test_t02_assessment_request_wraps_the_profile(profile: Profile) -> None:
    request = AssessmentRequest(profile=profile, round_id="round-2027")

    payload = request.model_dump(mode="json", by_alias=True)

    assert payload["profile"]["nationality"] == "MW"
    assert payload["roundId"] == "round-2027"
    assert "profile" in payload


def test_t02_assessment_request_requires_a_profile() -> None:
    with pytest.raises(ValidationError):
        AssessmentRequest.model_validate({"roundId": "round-2027"})


def test_t02_assessment_response_nests_the_result() -> None:
    result = AssessmentResult(
        opportunity_id="example-scheme",
        round_id="round-2027",
        outcome=AssessmentOutcome.INSUFFICIENT_INFORMATION,
        outcome_reason="Enter your profile to assess these requirements.",
        rules=(
            RuleAssessment(
                rule_id="rule-degree-recognition",
                result="insufficient_information",
                reason="We need your degree details first.",
            ),
        ),
    )

    payload = AssessmentResponse(assessment=result).model_dump(mode="json", by_alias=True)

    assert payload["assessment"]["outcome"] == "insufficient_information"
    assert payload["assessment"]["rules"][0]["ruleId"] == "rule-degree-recognition"


def test_t02_error_body_matches_the_agreed_shape() -> None:
    body = ErrorBody(
        code=ErrorCode.OPPORTUNITY_NOT_FOUND,
        message="We could not find that opportunity.",
        details=(FieldError(field="opportunityId", message="Unknown identifier."),),
    )

    assert body.model_dump(mode="json", by_alias=True) == {
        "code": "opportunity_not_found",
        "message": "We could not find that opportunity.",
        "details": [{"field": "opportunityId", "message": "Unknown identifier."}],
    }


def test_t02_error_body_details_are_optional() -> None:
    body = ErrorBody(code=ErrorCode.INTERNAL_ERROR, message="Something went wrong.")

    assert body.details is None
    assert body.model_dump(mode="json", by_alias=True) == {
        "code": "internal_error",
        "message": "Something went wrong.",
        "details": None,
    }


def test_t02_invalid_body_uses_the_error_shape(settings) -> None:
    """Validation failures must not leak a framework-shaped payload (AC-02)."""

    from app.config import Settings
    from app.main import create_app

    assert isinstance(settings, Settings)
    app = create_app(settings)

    @app.post("/api/__probe__/assessment")
    def _probe(payload: AssessmentRequest) -> AssessmentResponse:  # pragma: no cover
        raise AssertionError("validation should have run first")

    response = TestClient(app).post(
        "/api/__probe__/assessment", json={"roundId": "round-2027"}
    )

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "validation_error"
    assert body["details"][0]["field"] == "profile"
    assert "detail" not in body
