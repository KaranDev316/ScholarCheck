"""Explicit database initialization and publication of the audited launch record."""
import argparse
import os
from pathlib import Path
import psycopg
from app.storage.opportunities import create_schema
from app.publication.candidate import ExtractionProposal, extract_candidate
from app.publication.evidence_check import Adjudication, check_candidate
from app.publication.contracts import ValidationReport
from app.publication.store import publish
from app.collect.snapshot import load_artifact
import json


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['init','publish-launch'])
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    with psycopg.connect(os.environ['DATABASE_URL']) as conn:
        create_schema(conn)
        if args.action=='publish-launch':
            directory=root/'content/publication/cgrs-d'
            proposal=ExtractionProposal.model_validate_json((directory/'proposal.json').read_text())
            artifact=load_artifact(next((root/'content/snapshots').glob('nserc*.json')))
            candidate=extract_candidate(proposal,{artifact.snapshot.id:artifact.snapshot})
            recorded=ValidationReport.model_validate_json((directory/'complete-run/report.json').read_text())
            verdicts=[Adjudication.model_validate(v) for v in json.loads((directory/'adjudications.json').read_text())]
            report=check_candidate(candidate,verdicts,checked_at=recorded.checked_at)
            revision=publish(conn,candidate.opportunity,report,[artifact.snapshot])
            print(revision.model_dump_json())

if __name__=='__main__':
    main()
