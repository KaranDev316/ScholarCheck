"""Explicit public allowlist. No evidence, snapshots or revision metadata."""
from typing import Literal
from pydantic import Field
from app.domain.models import DomainModel, OfficialLinks as InternalLinks
from app.publication.facts import MaterialFacts, FactState

class Coverage(DomainModel):
    state: Literal['stated', 'unspecified'] = 'unspecified'
    detail: str | None = None

class FundingCoverage(DomainModel):
    tuition: Coverage = Coverage()
    living_costs: Coverage = Coverage()
    flights: Coverage = Coverage()

class Component(DomainModel):
    id: str
    label: str
    state: Literal['stated', 'unspecified']
    amount: str | None = None
    basis: str | None = None
    note: str | None = None
    conditions: tuple[str, ...] = ()

class Eligibility(DomainModel):
    id: str
    statement: str
    state: Literal['stated'] = 'stated'

class PublicRound(DomainModel):
    id: str
    round: str
    date_as_published: str
    status: str
    note: str

class Application(DomainModel):
    kind: Literal['confirm'] = 'confirm'
    note: str

class Links(DomainModel):
    summary: str
    requirements: str
    portal: str

class SourceCheck(DomainModel):
    checked_at: str
    result: Literal['matches'] = 'matches'

class Headline(DomainModel):
    component: str
    amount: str
    basis: str

class PublicOpportunity(DomainModel):
    id: str
    title: str
    provider: str
    country: str
    levels: tuple[str, ...]
    summary: str
    tags: tuple[str, ...] = ()
    headline: Headline | None = None
    coverage: FundingCoverage
    funding_type: str | None = None
    components: tuple[Component, ...]
    eligibility: tuple[Eligibility, ...]
    rounds: tuple[PublicRound, ...]
    application: Application
    links: Links
    source_check: SourceCheck

class CatalogueResponse(DomainModel):
    records: tuple[PublicOpportunity, ...]
    total: int
    offset: int
    limit: int

COUNTRIES = {'CA': 'Canada', 'AU': 'Australia', 'DE': 'Germany'}
LEVELS = {'doctoral': 'PhD', 'bachelor': "Bachelor's", 'research_master': "Master's", 'taught_master': "Master's"}


def public_record(record, report, checked_at):
    facts = report.facts
    def value(key):
        fact = facts.find(key)
        return fact.value if fact and fact.state is FactState.STATED else None
    coverage = {}
    for field, expected, kind in [('tuition', 'full tuition', 'tuition'), ('living_costs', 'living costs', 'living_support'), ('flights', 'flights', 'travel')]:
        supported = any(c.kind.value == kind and c.status.value == 'specified' and value(f'component:{c.id}.coverage') == expected for c in record.funding_components)
        coverage[field] = Coverage(state='stated' if supported else 'unspecified')
    cov = FundingCoverage(**coverage)
    funding_type = ('Fully funded' if all(v.state == 'stated' for v in coverage.values()) else
                    'Tuition + stipend' if cov.tuition.state == cov.living_costs.state == 'stated' else
                    'Tuition' if cov.tuition.state == 'stated' else None)
    components = []
    for c in record.funding_components:
        year = value(f'component:{c.id}.rate_year')
        components.append(Component(id=c.id, label='Award component' if c.kind.value == 'other' else c.kind.value.replace('_', ' ').title(),
            state='unspecified' if c.status.value == 'unspecified' else 'stated',
            amount=(f'{c.currency + " " if c.currency else ""}{c.amount:,f}{" (currency not stated)" if not c.currency else ""}' if c.amount is not None else None),
            basis='; '.join(x for x in [c.period, f'{year} rate' if year else None] if x) or None,
            note=c.description, conditions=c.conditions))
    rounds = []
    for r in record.rounds:
        deadline = value(f'round:{r.id}.deadline')
        stage = value(f'round:{r.id}.stage')
        # No year -> no inference of an open round. Client only ages complete dates.
        import re
        dated = bool(deadline and re.fullmatch(r'\d{1,2} [A-Za-z]+ \d{4}', deadline))
        rounds.append(PublicRound(id=r.id, round=r.label, date_as_published=deadline or 'Not stated',
            status='Deadline published' if dated else 'Confirm with provider',
            note='; '.join(x for x in [r.route, stage] if x)))
    headline = next((Headline(component=c.label, amount=c.amount, basis=c.basis or '') for c in components if c.amount), None)
    return PublicOpportunity(id=record.id, title=record.scheme_name, provider=record.funder,
        country=', '.join(COUNTRIES.get(c,c) for c in record.destinations),
        levels=tuple(dict.fromkeys(LEVELS[p.degree_level.value] for p in record.programmes)),
        summary=record.summary, headline=headline, coverage=cov, funding_type=funding_type,
        components=tuple(components), eligibility=tuple(Eligibility(id=r.id, statement=r.requirement) for r in record.eligibility_rules),
        rounds=tuple(rounds), application=Application(note='Confirm the route and deadlines for your circumstances with the official provider.'),
        links=Links(summary=str(record.links.summary_url),requirements=str(record.links.requirements_url),portal=str(record.links.portal_url)),
        source_check=SourceCheck(checked_at=checked_at.isoformat()))
