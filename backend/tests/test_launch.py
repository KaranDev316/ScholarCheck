"""Real retained-source publication and public/monitoring acceptance tests."""
import json
from datetime import timedelta
from pathlib import Path
from decimal import Decimal

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.collect.snapshot import load_artifact
from app.config import Settings
from app.main import create_app
from app.publication.candidate import ExtractionProposal, extract_candidate
from app.publication.evidence_check import Adjudication, check_candidate
from app.publication.contracts import ValidationReport, DecisionType, CheckResult
from app.publication.facts import MaterialFacts, MaterialFact, FactReading
from app.publication.gates import evaluate, PublicationBlocked
from app.publication.register import load_register
from app.publication.store import publish
from app.publication.values import amount_in_text, value_in_text
from app.monitoring.worker import monitor
from tests.publication_helpers import sample_record, build_report, build_snapshots, no_findings

ROOT = Path(__file__).resolve().parents[2]
LAUNCH = ROOT/'content/publication/cgrs-d'


def launch():
    proposal = ExtractionProposal.model_validate_json((LAUNCH/'proposal.json').read_text())
    artifact = load_artifact(next((ROOT/'content/snapshots').glob('nserc*.json')))
    candidate = extract_candidate(proposal,{artifact.snapshot.id: artifact.snapshot})
    adjudications = [Adjudication.model_validate(v) for v in json.loads((LAUNCH/'adjudications.json').read_text())]
    original = ValidationReport.model_validate_json((LAUNCH/'complete-run/report.json').read_text())
    report = check_candidate(candidate, adjudications, checked_at=original.checked_at)
    return candidate.opportunity,report,artifact


@pytest.mark.parametrize('amount,text,expected', [
    ('40000','140,000',False), ('40000','400.00',False),('40000','40,000',True),
    ('24067.80','24 067,80 $',True),('40000','40 students and 000 awards',False),
    ('40000','40000.00',True),('40','40,000',False),('40000','140000',False),('40000','-40,000',False),('40','40%',False),('40','40 %',False),('40000','CAD - 40,000',False),('40','40 percent',False)])
def test_numeric_boundaries(amount,text,expected):
    assert amount_in_text(Decimal(amount),text) is expected


def test_changed_snapshot_context_cannot_reuse_report():
    r,p,a=launch()
    changed=a.snapshot.model_copy(update={'body':a.snapshot.body+' New restriction.'})
    d=evaluate(r,p,{changed.id:changed},register=load_register())
    assert d.decision is DecisionType.HOLD
    assert any('exact snapshot' in x for x in d.reasons)


def test_conflicting_year_holds_even_without_positive_display():
    r=sample_record(); s=build_snapshots(r); p=build_report(r,s)
    f=MaterialFact(subject='component:fund-living',kind='rate_year',state='conflicting',reason='Sources disagree',readings=tuple(FactReading(value=v,evidence_id='ev-value',snapshot_id=s[0].id,excerpt=s[0].body) for v in ['2026','2027']))
    facts=MaterialFacts(facts=tuple(f if old.key==f.key else old for old in p.facts.facts))
    p=p.model_copy(update={'facts':facts,'facts_hash':facts.fingerprint})
    d=evaluate(r,p,{s[0].id:s[0]},register=no_findings())
    assert any('conflicting material fact' in reason for reason in d.reasons)


def test_currency_period_and_wrong_scholarship_do_not_publish():
    r=sample_record(); s=build_snapshots(r)
    for update in [{'currency':'USD'}, {'period':'per month'}]:
        changed=r.model_copy(update={'funding_components':(r.funding_components[0].model_copy(update=update),)})
        assert evaluate(changed,build_report(changed,s),{s[0].id:s[0]},register=no_findings()).decision is DecisionType.HOLD
    p=build_report(r,s)
    checks=tuple(c.model_copy(update={'applies_to':c.applies_to.model_copy(update={'scholarship':'Different scholarship'})}) if c.applies_to else c for c in p.checks)
    assert evaluate(r,p.model_copy(update={'checks':checks}),{s[0].id:s[0]},register=no_findings()).decision is DecisionType.HOLD


def test_real_candidate_publication_rejection_and_public_contract(test_dsn):
    r,p,a=launch()
    with psycopg.connect(test_dsn) as conn:
        first=publish(conn,r,p,[a.snapshot])
        assert first.revision==1
        # A rejected claim must preserve the published version and checked date.
        bad=p.model_copy(update={'checks':tuple(c.model_copy(update={'result':CheckResult.UNSUPPORTED,'reason':'Wrong claim'}) for c in p.checks)})
        with pytest.raises(PublicationBlocked): publish(conn,r,bad,[a.snapshot])
        assert conn.execute('SELECT count(*) FROM opportunity_revisions').fetchone()[0]==1
    settings=Settings('production',('https://scholarcheck.test',),test_dsn,report_hash_key='test-secret')
    with TestClient(create_app(settings)) as client:
        body=client.get('/api/v1/opportunities/cgsd-doctoral').json()
        assert body['sourceCheck']['result']=='matches'
        assert body['fundingType'] is None
        assert all(x['status']=='Confirm with provider' for x in body['rounds'])
        text=json.dumps(body)
        for forbidden in ['evidence','snapshot','policyVersion','revision','passage','retrievedAt']:
            assert forbidden not in text
        assert client.get('/api/v1/opportunities?q=doctoral&country=Canada&level=PhD').json()['total']==1
        assert client.get('/api/v1/opportunities?country=Australia').json()['total']==0
        assert client.get('/api/v1/opportunities?funding=Fully%20funded').json()['total']==0
        assert client.get('/api/v1/opportunities?limit=0').status_code==422
        assert client.get('/api/v1/opportunities/rmit-research-stipend').status_code==404
        assert client.post('/api/v1/opportunities/cgsd-doctoral/reports',json={'reason':'The amount'},headers={'Origin':'https://evil.test'}).status_code==403
        assert client.post('/api/v1/opportunities/cgsd-doctoral/reports', content='x'*9000, headers={'Content-Type':'application/json'}).status_code==413
        for _ in range(5):
            assert client.post('/api/v1/opportunities/cgsd-doctoral/reports',json={'reason':'The amount','details':'Please recheck.'}).status_code==202
        assert client.post('/api/v1/opportunities/cgsd-doctoral/reports',json={'reason':'The amount'}).status_code==429
    with psycopg.connect(test_dsn) as conn:
        assert conn.execute('SELECT count(*) FROM problem_reports').fetchone()[0]==5


def test_monitor_unchanged_hold_retry_preserves_published_revision(test_dsn,tmp_path):
    r,p,a=launch()
    with psycopg.connect(test_dsn) as conn:
        publish(conn,r,p,[a.snapshot])
        assert monitor(conn,r.id,fetch=lambda _:a,audit_root=tmp_path,force=True)=='unchanged'
        changed=a.model_copy(update={'snapshot':a.snapshot.model_copy(update={'id':'changed-source','body':a.snapshot.body+' Changed eligibility.'})})
        assert monitor(conn,r.id,fetch=lambda _:changed,audit_root=tmp_path,force=True)=='held'
        def fail(_): raise OSError('offline')
        assert monitor(conn,r.id,fetch=fail,audit_root=tmp_path,force=True)=='failed'
        state=conn.execute('SELECT revision,source_checked_at,freshness FROM publication_state').fetchone()
        assert state==(1,p.checked_at,'stale')
        assert conn.execute('SELECT failures FROM monitor_state').fetchone()[0]==1
        assert monitor(conn,r.id,fetch=fail,audit_root=tmp_path)=='not_due'
        assert conn.execute('SELECT count(*) FROM monitor_runs').fetchone()[0]==3


def test_monitor_validates_changed_amount_and_publishes_or_holds(test_dsn,tmp_path):
    r,p,a=launch()
    from app.collect.snapshot import snapshot_id
    from datetime import UTC, datetime
    body=a.snapshot.body.replace('$40,000','$41,000')
    snapshot=a.snapshot.model_copy(update={'body':body,'id':snapshot_id(str(a.snapshot.url),body),'retrieved_at':datetime.now(UTC)})
    changed=a.model_copy(update={'snapshot':snapshot})
    proposal=json.loads((LAUNCH/'proposal.json').read_text())
    proposal['opportunity']['summary']=proposal['opportunity']['summary'].replace('$40,000','$41,000')
    proposal['opportunity']['funding_components'][0]['amount']='41000'
    proposal['opportunity']['last_retrieved_at']=snapshot.retrieved_at.isoformat()
    for e in proposal['opportunity']['evidence']:
        e['retrieved_at']=snapshot.retrieved_at.isoformat()
        e['passage']=e['passage'].replace('$40,000','$41,000')
    for fact in proposal['facts']:
        for reading in fact['readings']:
            reading['snapshot_id']=snapshot.id
            reading['excerpt']=reading['excerpt'].replace('$40,000','$41,000')
            if fact['kind']=='amount': reading['value']='41000'
            if fact['kind']=='summary': reading['value']=reading['value'].replace('$40,000','$41,000')
    verdicts=json.loads((LAUNCH/'adjudications.json').read_text())
    for verdict in verdicts: verdict['snapshot_id']=snapshot.id
    with psycopg.connect(test_dsn) as conn:
        publish(conn,r,p,[a.snapshot])
        def reject(_):
            failed=[dict(v) for v in verdicts]
            failed[0].update(result='unsupported',reason='Unconfirmed amount',applies_to=None)
            return failed
        assert monitor(conn,r.id,fetch=lambda _:changed,extractor=lambda _:proposal,checker=reject,audit_root=tmp_path,force=True)=='held'
        assert conn.execute('SELECT revision FROM publication_state').fetchone()[0]==1
        assert monitor(conn,r.id,fetch=lambda _:changed,extractor=lambda _:proposal,checker=lambda _:verdicts,audit_root=tmp_path,force=True)=='published'
        assert conn.execute('SELECT revision FROM publication_state').fetchone()[0]==2
        stored=conn.execute('SELECT payload FROM opportunity_revisions WHERE revision=2').fetchone()[0]
        assert stored['funding_components'][0]['amount']=='41000'
        assert monitor(conn,r.id,fetch=lambda _:changed,audit_root=tmp_path,force=True)=='unchanged'
        assert conn.execute('SELECT count(*) FROM opportunity_revisions').fetchone()[0]==2


@pytest.mark.parametrize('currency,text,expected', [
    ('CAD', 'C$40,000', True), ('AUD', 'A$44,293', True),
    ('CAD', '$40,000', False), ('USD', 'CAD 40,000', False),
])
def test_currency_symbols_and_ambiguity(currency, text, expected):
    assert value_in_text('currency', currency, text) is expected


def test_monitor_respects_the_publication_lock(test_dsn, tmp_path):
    r,p,a=launch()
    with psycopg.connect(test_dsn) as setup:
        publish(setup,r,p,[a.snapshot])
    with psycopg.connect(test_dsn) as publisher, psycopg.connect(test_dsn) as worker:
        publisher.execute('SELECT pg_advisory_xact_lock(hashtext(%s))', (r.id,))
        def never_fetch(_):
            raise AssertionError('Locked records must not be fetched or overwritten')
        assert monitor(worker,r.id,fetch=never_fetch,audit_root=tmp_path,force=True)=='busy'
