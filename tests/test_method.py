import json

import pytest
from asynctest import mock
from marshmallow import Schema, fields
from starlette.requests import Request
from starlette.responses import Response

from star_resty import Method
from star_resty.exceptions import DumpError
from .utils.method import CreateUser


@pytest.mark.asyncio
async def test_create_user():
    request = mock.MagicMock(spec_set=Request)
    request.path_params = {'id': 1}
    request.body.return_value = json.dumps({'name': 'Name', 'email': 'email@mail.com'}).encode('utf8')

    endpoint = CreateUser.as_endpoint()
    resp = await endpoint(request)
    assert resp is not None
    assert isinstance(resp, Response)
    assert resp.status_code == 201
    assert resp.media_type == 'application/json'
    body = resp.body
    assert body is not None
    user = json.loads(body)
    assert user == {'name': 'Name', 'email': 'email@mail.com', 'id': 1}


@pytest.mark.asyncio
async def test_raise_dump_error():
    class ResponseSchema(Schema):
        id = fields.Integer()

    class TestMethod(Method):
        response_schema = ResponseSchema

        async def execute(self):
            return {'id': 'test'}

    request = mock.MagicMock(spec_set=Request)
    endpoint = TestMethod.as_endpoint()
    with pytest.raises(DumpError):
        await endpoint(request)
