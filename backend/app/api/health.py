"""Health endpoint. Public, unauthenticated, no personal data (S01)."""

from fastapi import APIRouter, Request

from app.config import Settings
from app.domain.models import DomainModel

router = APIRouter(tags=["system"])


class HealthResponse(DomainModel):
    status: str
    service: str
    environment: str


@router.get("/health", response_model=HealthResponse)
def read_health(request: Request) -> HealthResponse:
    """Report that the service is up; used by the frontend status panel."""

    settings: Settings = request.app.state.settings
    return HealthResponse(
        status="ok",
        service="scholarcheck-api",
        environment=settings.app_env,
    )
