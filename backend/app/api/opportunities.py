"""Published revisions only, with a deliberately small public contract."""
import hashlib
import hmac
from uuid import uuid4
import psycopg
from fastapi import APIRouter, Request, Query
from pydantic import Field
from app.api.errors import ApiError, ErrorCode
from app.domain.models import DomainModel, Opportunity
from app.models.public import PublicOpportunity, CatalogueResponse, public_record
from app.publication.contracts import ValidationReport

router = APIRouter(prefix='/v1/opportunities', tags=['opportunities'])


def connect(request):
    dsn = request.app.state.settings.database_url
    if not dsn:
        raise ApiError(503, ErrorCode.SERVICE_UNAVAILABLE, 'Opportunity data is unavailable.')
    return psycopg.connect(dsn)


def published(conn, identifier=None):
    rows = conn.execute('''SELECT r.payload, r.report, r.checked_at FROM opportunity_revisions r
        JOIN publication_state s ON (s.opportunity_id = r.opportunity_id AND s.revision = r.revision)
        WHERE s.assurance = 'source_checked' AND (%s::text IS NULL OR r.opportunity_id = %s)
        ORDER BY r.opportunity_id''', (identifier, identifier)).fetchall()
    return [public_record(Opportunity.model_validate(p), ValidationReport.model_validate(r), t) for p,r,t in rows]


def unavailable(exc):
    return ApiError(503, ErrorCode.SERVICE_UNAVAILABLE, 'Opportunity data is unavailable.')


@router.get('', response_model=CatalogueResponse)
def catalogue(request: Request, q: str = Query('', max_length=200), country: str = Query('', max_length=80),
              level: str = Query('', max_length=40), funding: str = Query('', max_length=40),
              offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    try:
        with connect(request) as conn:
            records = published(conn)
    except psycopg.Error as exc:
        raise unavailable(exc) from exc
    records = [r for r in records if (not q or q.casefold() in f'{r.title} {r.provider} {r.summary}'.casefold())
               and (not country or country.casefold() == r.country.casefold())
               and (not level or level in r.levels) and (not funding or funding == r.funding_type)]
    return CatalogueResponse(records=tuple(records[offset:offset+limit]), total=len(records), offset=offset, limit=limit)


@router.get('/{opportunity_id}', response_model=PublicOpportunity)
def read_opportunity(opportunity_id: str, request: Request):
    try:
        with connect(request) as conn:
            records = published(conn, opportunity_id)
    except psycopg.Error as exc:
        raise unavailable(exc) from exc
    if not records:
        raise ApiError(404, ErrorCode.OPPORTUNITY_NOT_FOUND, 'We could not find that opportunity.')
    return records[0]


class ProblemReport(DomainModel):
    reason: str = Field(min_length=1, max_length=80)
    details: str = Field(default='', max_length=2000)
    website: str = Field(default='', max_length=200)  # honeypot


@router.post('/{opportunity_id}/reports', status_code=202)
def report_problem(opportunity_id: str, body: ProblemReport, request: Request):
    settings = request.app.state.settings
    origin = request.headers.get('origin')
    if origin and origin not in settings.cors_allowed_origins:
        raise ApiError(403, ErrorCode.INVALID_REQUEST, 'This origin is not allowed.')
    if body.website:
        raise ApiError(400, ErrorCode.INVALID_REQUEST, 'Could not accept this report.')
    if not settings.report_hash_key:
        raise ApiError(503, ErrorCode.SERVICE_UNAVAILABLE, 'Reports are temporarily unavailable.')
    client = request.client.host if request.client else 'unknown'
    digest = hmac.new(settings.report_hash_key.encode(), client.encode(), hashlib.sha256).hexdigest()
    identifier = uuid4()
    try:
        with connect(request) as conn:
            conn.execute('SELECT pg_advisory_xact_lock(hashtext(%s))', (digest,))
            if not published(conn, opportunity_id):
                raise ApiError(404, ErrorCode.OPPORTUNITY_NOT_FOUND, 'We could not find that opportunity.')
            count = conn.execute("SELECT count(*) FROM problem_reports WHERE client_hash=%s AND created_at > now() - interval '1 hour'", (digest,)).fetchone()[0]
            if count >= 5:
                raise ApiError(429, ErrorCode.INVALID_REQUEST, 'Too many reports. Please try again later.')
            conn.execute('INSERT INTO problem_reports (id, opportunity_id, reason, details, client_hash) VALUES (%s,%s,%s,%s,%s)', (identifier, opportunity_id, body.reason, body.details, digest))
    except psycopg.Error as exc:
        raise unavailable(exc) from exc
    return {'id': str(identifier), 'message': 'Report received. Thank you.'}
