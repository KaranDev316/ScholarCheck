"""Read opportunity reference data without granting publication assurance."""

import psycopg
from fastapi import APIRouter, Request

from app.api.errors import ApiError, ErrorCode
from app.config import Settings
from app.models.opportunity import OpportunityResponse, PublicationMetadata
from app.storage.opportunities import get_opportunity

router = APIRouter(prefix="/v1/opportunities", tags=["opportunities"])


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def read_opportunity(opportunity_id: str, request: Request) -> OpportunityResponse:
    settings: Settings = request.app.state.settings
    if not settings.database_url:
        raise ApiError(
            503, ErrorCode.SERVICE_UNAVAILABLE, "Opportunity data is unavailable."
        )

    try:
        with psycopg.connect(settings.database_url) as conn:
            loaded = get_opportunity(conn, opportunity_id)
    except psycopg.Error as exc:
        raise ApiError(
            503, ErrorCode.SERVICE_UNAVAILABLE, "Opportunity data is unavailable."
        ) from exc

    if loaded is None:
        raise ApiError(
            404, ErrorCode.OPPORTUNITY_NOT_FOUND, "We could not find that opportunity."
        )

    opportunity, raw_metadata = loaded
    publication = PublicationMetadata.model_validate(raw_metadata)
    is_published = publication.assurance.value in {"source_checked", "human_verified"}
    if not is_published and settings.app_env not in {"development", "test"}:
        raise ApiError(
            404, ErrorCode.OPPORTUNITY_NOT_FOUND, "We could not find that opportunity."
        )
    return OpportunityResponse(
        opportunity=opportunity,
        publication=publication,
        is_published=is_published,
    )
