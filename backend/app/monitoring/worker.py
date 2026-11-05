"""One-record worker: unchanged, validated revision, hold or retry.

Run from a scheduler every hour. PostgreSQL locks prevent overlapping runs;
next_run_at provides a daily cadence and bounded exponential failure backoff.
Only URLs already backing the published record may be fetched.
"""
import argparse
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from app.collect.snapshot import collect, write_artifact, SnapshotExists
from app.publication.contracts import DecisionType
from app.publication.pipeline import validate, command_pass
from app.publication.policy import is_approved_source, APPROVED_SOURCE_HOSTS
from app.publication.store import publish, read_snapshot


def monitored_fetch(url):
    return collect(url, allowed_hosts=APPROVED_SOURCE_HOSTS)


def monitor(conn, opportunity_id, *, fetch=monitored_fetch, extractor=None, checker=None,
            audit_root=Path('var/monitoring'), force=False, now=None):
    now = now or datetime.now(UTC)
    # A transaction lock covers fetch, validation and publication; a second worker
    # returns promptly rather than doing duplicate network or model work.
    with conn.transaction():
        if not conn.execute('SELECT pg_try_advisory_xact_lock(hashtext(%s))', (opportunity_id,)).fetchone()[0]:
            return 'busy'
        current = conn.execute("SELECT revision FROM publication_state WHERE opportunity_id=%s AND assurance='source_checked'", (opportunity_id,)).fetchone()
        if not current:
            raise ValueError('Monitoring requires a published record')
        conn.execute('INSERT INTO monitor_state(opportunity_id) VALUES (%s) ON CONFLICT DO NOTHING', (opportunity_id,))
        due, failures, previous_hashes = conn.execute('SELECT next_run_at, failures, last_hashes FROM monitor_state WHERE opportunity_id=%s FOR UPDATE', (opportunity_id,)).fetchone()
        if not force and due > now:
            return 'not_due'
        old = [read_snapshot(conn, row[0]) for row in conn.execute('SELECT snapshot_id FROM revision_snapshots WHERE opportunity_id=%s AND revision=%s', (opportunity_id,current[0]))]
        urls = sorted({str(s.url) for s in old})
        baseline = {str(s.url): s.content_hash for s in old}
        identifier = uuid4()
        outcome, detail, hashes = 'failed', '', {}
        try:
            snapshots=[]
            for url in urls:
                if not is_approved_source(url, APPROVED_SOURCE_HOSTS):
                    raise ValueError('Source no longer approved')
                artifact=fetch(url)
                if not is_approved_source(artifact.snapshot.url, APPROVED_SOURCE_HOSTS):
                    raise ValueError('Redirect destination is not approved')
                try:
                    write_artifact(artifact, audit_root/'snapshots')
                except SnapshotExists as exists:
                    if not exists.same_text:
                        raise
                snapshots.append(artifact.snapshot)
                hashes[url]=artifact.snapshot.content_hash
            if hashes == baseline:
                outcome, detail = 'unchanged', 'Retained text is unchanged; no extraction or publication work.'
            elif hashes == previous_hashes and not force:
                outcome, detail = 'held', 'Previously held source content is unchanged; awaiting new source evidence.'
            elif extractor is None or checker is None:
                outcome, detail = 'held', 'Source changed; extraction and checking commands are not configured.'
            else:
                previous=conn.execute('SELECT payload FROM opportunity_revisions WHERE opportunity_id=%s AND revision=%s',(opportunity_id,current[0])).fetchone()[0]
                candidate, report, decision=validate(snapshots,extractor,checker,audit_root/str(identifier),previous_record=previous)
                if candidate.opportunity.id != opportunity_id:
                    raise ValueError('Extraction changed the registered opportunity identity')
                if decision.decision is DecisionType.PUBLISH:
                    with conn.transaction():
                        publish(conn,candidate.opportunity,report,snapshots)
                    outcome,detail='published','Published a supported revision from changed source content.'
                else:
                    outcome,detail='held','; '.join(decision.reasons)
        except ValueError as exc:
            outcome,detail='held',f'Candidate or evidence check refused ({type(exc).__name__}); last supported revision retained.'
        except Exception as exc:
            # Persist a safe failure class, not a transport message containing credentials.
            outcome,detail='failed',f'Collection or validation failed ({type(exc).__name__}); last supported revision retained.'
        failures = failures+1 if outcome=='failed' else 0
        delay = min(24, 2 ** min(failures,5)) if failures else 24
        conn.execute('UPDATE monitor_state SET next_run_at=%s, failures=%s, last_hashes=%s WHERE opportunity_id=%s',
                     (now+timedelta(hours=delay),failures,Jsonb(hashes if outcome!='failed' else previous_hashes),opportunity_id))
        freshness = 'stale' if outcome=='failed' else 'needs_recheck' if outcome=='held' else 'current'
        conn.execute('UPDATE publication_state SET freshness=%s WHERE opportunity_id=%s',(freshness,opportunity_id))
        conn.execute('INSERT INTO monitor_runs(id,opportunity_id,attempted_at,outcome,detail,snapshot_hashes) VALUES (%s,%s,%s,%s,%s,%s)',
                     (identifier,opportunity_id,now,outcome,detail,Jsonb(hashes)))
        return outcome


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('opportunity_id')
    parser.add_argument('--force',action='store_true')
    parser.add_argument('--loop', action='store_true')
    args=parser.parse_args()
    from app.publication.model_pass import configured_pass
    import time
    while True:
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            print(monitor(conn,args.opportunity_id,force=args.force,
                extractor=configured_pass('EXTRACT'), checker=configured_pass('CHECK')), flush=True)
        if not args.loop:
            break
        time.sleep(3600)

if __name__=='__main__':
    main()
