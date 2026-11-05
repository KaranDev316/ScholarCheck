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
    assert 'previous_response_id' not in requests[0]
    assert 'tools' not in requests[0]
    assert adapter.last_metadata['id']=='response-test'


@pytest.mark.parametrize('payload',[
    {'status':'incomplete'},
    {'status':'completed','output':[{'type':'message','content':[{'type':'refusal','refusal':'No'}]}]},
    {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'{"publish":true}'}]}]},
])
def test_refusal_or_incomplete_output_cannot_produce_candidate(payload):
    adapter=ModelPass('configured-model','test-key',transport=lambda *a,**k:io.BytesIO(json.dumps(payload).encode()))
    with pytest.raises(ValueError): adapter({'instructions':'Check','schema':{}})
