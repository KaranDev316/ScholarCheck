"""Structured error bodies and exception handlers.

Shape (CONTEXT section 6): ``{code, message, details?}``. Messages are written
for a non-technical reader; stack traces are never returned.

This shape is a proposal for the T02/T07 gate recorded in
``docs/slices/S01/VERIFICATION.md`` section 5. It is implemented for framework
errors only; the assessment endpoint arrives in T07.
"""

from collections.abc import Iterable
from enum import StrEnum

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.models import DomainModel


class ErrorCode(StrEnum):
    """Codes the client may branch on. Additions need a contract note."""

    VALIDATION_ERROR = "validation_error"
    OPPORTUNITY_NOT_FOUND = "opportunity_not_found"
    INVALID_PROFILE = "invalid_profile"
    ASSESSMENT_FAILED = "assessment_failed"
    NOT_FOUND = "not_found"
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"


class FieldError(DomainModel):
    """A single problem, anchored to a field the client can highlight."""

    field: str
    message: str


class ErrorBody(DomainModel):
    """Body of every non-2xx JSON response."""

    code: ErrorCode | str
    message: str
    details: tuple[FieldError, ...] | None = None


class ApiError(Exception):
    """Raised by route code when a request cannot be served."""

    def __init__(
        self,
        status_code: int,
        code: ErrorCode,
        message: str,
        details: Iterable[FieldError] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = tuple(details) if details else None

    def to_response(self) -> JSONResponse:
        body = ErrorBody(code=self.code, message=self.message, details=self.details)
        return JSONResponse(
            status_code=self.status_code,
            content=body.model_dump(mode="json", by_alias=True),
        )


def _validation_details(payload: list[dict[str, object]]) -> tuple[FieldError, ...]:
    details: list[FieldError] = []
    for item in payload:
        location = item.get("loc", ())
        parts = [str(part) for part in location if part not in ("body", "query")]
        details.append(
            FieldError(
                field=".".join(parts) or "request",
                message=str(item.get("msg", "This value is not valid.")),
            )
        )
    return tuple(details)


def register_exception_handlers(app: FastAPI) -> None:
    """Register handlers so every failure uses the agreed error body."""

    @app.exception_handler(ApiError)
    async def _handle_api_error(_request: Request, exc: ApiError) -> JSONResponse:
        return exc.to_response()

    @app.exception_handler(RequestValidationError)
    async def _handle_request_validation(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        body = ErrorBody(
            code=ErrorCode.VALIDATION_ERROR,
            message="Some of the details sent are not valid.",
            details=_validation_details(list(exc.errors())),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=body.model_dump(mode="json", by_alias=True),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http_error(
        _request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code = ErrorCode.NOT_FOUND if exc.status_code == 404 else ErrorCode.INTERNAL_ERROR
        message = (
            "We could not find that page."
            if exc.status_code == 404
            else "Something went wrong on our side."
        )
        body = ErrorBody(code=code, message=message)
        return JSONResponse(
            status_code=exc.status_code,
            content=body.model_dump(mode="json", by_alias=True),
        )
