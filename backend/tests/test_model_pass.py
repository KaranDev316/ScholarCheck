import io
import json
import pytest
from app.publication.model_pass import ModelPass


def test_model_adapter_is_stateless_and_validates_envelope():
    requests=[]
    def transport(request,timeout):
        requests.append(json.loads(request.data))
        return io.BytesIO(json.dumps({'id':'response-test','model':'configured-model','status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'{"result": []}'}]}]}).encode())
    adapter=ModelPass('configured-model','test-key',transport=transport)
    assert adapter({'instructions':'Independently check evidence','schema':{}})==[]
    assert requests[0]['store'] is False
    assert 'json' in requests[0]['input'].lower()
    assert 'previous_response_id' not in requests[0]
    assert 'tools' not in requests[0]
    assert adapter.last_metadata['id']=='response-test'


def test_model_adapter_uses_strict_schema_and_utf8_input():
    from app.publication.candidate import ExtractionProposal
    requests=[]
    def transport(request,timeout):
        requests.append(json.loads(request.data))
        return io.BytesIO(json.dumps({'id':'response-test','model':'configured-model','status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'{"result": {"ok": true}}'}]}]}).encode())
    adapter=ModelPass('configured-model','test-key',transport=transport)
    assert adapter({'task':'extract','instructions':'Extract','snapshots':[{'body':'Doctoral – program'}],'schema':ExtractionProposal.model_json_schema()})=={'ok':True}
    fmt=requests[0]['text']['format']
    assert fmt['type']=='json_schema'
    assert fmt['strict'] is True
    assert 'Doctoral – program' in requests[0]['input']


@pytest.mark.parametrize('payload',[
    {'status':'incomplete'},
    {'status':'completed','output':[{'type':'message','content':[{'type':'refusal','refusal':'No'}]}]},
    {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'{"publish":true}'}]}]},
])
def test_refusal_or_incomplete_output_cannot_produce_candidate(payload):
    adapter=ModelPass('configured-model','test-key',transport=lambda *a,**k:io.BytesIO(json.dumps(payload).encode()))
    with pytest.raises(ValueError): adapter({'instructions':'Check','schema':{}})


def test_extraction_selects_exact_source_blocks_without_copying_quotes():
    from app.publication.candidate import ExtractionProposal
    requests = []
    def transport(request, timeout):
        requests.append(json.loads(request.data))
        return io.BytesIO(json.dumps({'status': 'completed', 'output': [{'type': 'message', 'content': [
            {'type': 'output_text', 'text': json.dumps({'result': {'passage': '1', 'excerpt': '0'}})}]}]}).encode())
    adapter = ModelPass('test', 'key', transport=transport)
    result = adapter({'task': 'extract', 'instructions': 'Extract',
                      'snapshots': [{'body': 'First sentence.\nTo the limit of available funding, awards are offered.'}],
                      'schema': ExtractionProposal.model_json_schema()})
    assert result == {'passage': 'To the limit of available funding, awards are offered.', 'excerpt': 'First sentence.'}
    wire = json.loads(requests[0]['input'].split('\n', 1)[1])
    assert 'schema' not in wire and 'instructions' not in wire
    assert 'body' not in wire['snapshots'][0]


def test_checker_returns_ids_and_restores_bindings_without_changing_verdicts():
    from pydantic import TypeAdapter
    from app.publication.evidence_check import Adjudication
    from app.publication.model_pass import _checker_protocol
    payload = {'task': 'check', 'instructions': 'Check', 'schema': TypeAdapter(list[Adjudication]).json_schema(),
               'snapshots': [{'body': 'Full source context remains here.'}],
               'candidate': {'opportunity': {'evidence': [{'passage': 'Repeated quote'}]}, 'facts': {'facts': [
                   {'subject': 'record', 'kind': 'summary', 'state': 'stated', 'readings': [
                       {'value': 'claim', 'snapshot_id': 'source-1', 'evidence_id': 'evidence-1', 'excerpt': 'Repeated quote'}]}]}}}
    wire, bindings = _checker_protocol(payload)
    assert wire['excerpts'] == {'0': 'Repeated quote'}
    assert 'excerpt' not in wire['candidate']['facts']['facts'][0]['readings'][0]
    assert set(wire['schema']['$defs']['Adjudication']['properties']) == {'result', 'reason', 'appliesTo', 'reading_id'}
    assert payload['candidate']['opportunity']['evidence'][0]['passage'] == 'Repeated quote'
    def transport(request, timeout):
        output = [{'reading_id': '0', 'result': 'unsupported', 'reason': 'Wrong applicant category', 'applies_to': None}]
        return io.BytesIO(json.dumps({'status': 'completed', 'usage': {'input_tokens': 20, 'output_tokens': 10, 'total_tokens': 30},
            'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps({'result': output})}]}]}).encode())
    adapter = ModelPass('test', 'key', transport=transport)
    result = adapter(payload)
    assert result[0]['excerpt'] == bindings['0']['excerpt']
    assert result[0]['result'] == 'unsupported'
    assert adapter.last_metadata['usage']['total_tokens'] == 30


def test_pipeline_retains_usage_even_when_extraction_fails(tmp_path):
    from app.publication.pipeline import validate
    class FailedPass:
        last_metadata = {'usage': {'input_tokens': 8, 'output_tokens': 3, 'total_tokens': 11}}
        def __call__(self, payload):
            raise ValueError('Invalid model output')
    audit = tmp_path / 'audit'
    with pytest.raises(ValueError, match='Invalid model output'):
        validate([], FailedPass(), lambda _: [], audit)
    usage = json.loads((audit / 'usage.json').read_text())
    assert usage['totals']['total_tokens'] == 11
    assert usage['passes']['extraction']['input_tokens'] == 8
