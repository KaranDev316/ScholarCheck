"""Run against the actual deployed origin, optionally creating one problem report."""
import argparse
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError

parser=argparse.ArgumentParser()
parser.add_argument('origin')
parser.add_argument('--report',action='store_true')
parser.add_argument('--require-contact',action='store_true')
args=parser.parse_args()
base=args.origin.rstrip('/')
def get(path):
    with urlopen(base+path,timeout=20) as response:
        return json.load(response)
with urlopen(base,timeout=20) as response:
    assert '<div id="root"></div>' in response.read().decode()
assert get('/api/health')
site=get('/api/site')
if args.require_contact: assert site['contactEmail'] and '@' in site['contactEmail']
records=get('/api/v1/opportunities')['records']
assert records, 'No published launch record'
record=get('/api/v1/opportunities/'+records[0]['id'])
assert record['sourceCheck']['checkedAt']
for key in ['evidence','report','snapshotIds','validationPolicyVersion','revision']:
    assert key not in json.dumps(record)
assert get('/api/v1/opportunities?q=unmatchable-smoke-query')['total']==0
try:
    get('/api/v1/opportunities/rmit-research-stipend')
    raise AssertionError('RMIT must remain private')
except HTTPError as e:
    assert e.code==404
if args.report:
    payload=json.dumps({'reason':'Smoke test','details':'Deployment acceptance test.'}).encode()
    request=Request(base+'/api/v1/opportunities/'+record['id']+'/reports',data=payload,headers={'Content-Type':'application/json','Origin':base})
    with urlopen(request,timeout=20) as response:
        assert response.status==202
print(json.dumps({'origin':base,'publishedRecord':record['id'],'smoke':'passed','reportTested':args.report,'contactRequired':args.require_contact}))
