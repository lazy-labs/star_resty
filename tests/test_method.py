import json
from dataclasses import dataclass
from typing import Mapping, Optional

import pytest
from asynctest import mock
from marshmallow import Schema, fields, post_load
from starlette.requests import Request
from starlette.responses import Response

from star_resty import Method, path_schema, json_payload
from star_resty.exceptions import DumpError
from .utils.method import CreateUser, BodySchema


@pytest.mark.asyncio
async def test_create_user():
    request = mock.MagicMock(spec_set=Request)
    request.path_params = {'id': 1}
    request.body.return_value = json.dumps({'name': 'Name', 'email': 'email@mail.com'}).encode('utf8')

    user = await execute(CreateUser, request, status_code=201)
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


@pytest.mark.asyncio
async def test_response_schema_cls():
    class TestMethod(Method):
        class Response(Schema):
            id = fields.Integer()

        async def execute(self):
            return {'id': 1}

    request = mock.MagicMock(spec_set=Request)
    user = await execute(TestMethod, request)
    assert user == {'id': 1}


@pytest.mark.asyncio
async def test_parse_dataclass():
    class PathParams(Schema):
        group_id = fields.Integer(required=True)

        @post_load()
        def load(self, data, **_):
            return data.get('group_id')

    class TestMethod(Method):
        @dataclass()
        class Payload:
            group_id: path_schema(PathParams, int)
            body: Optional[json_payload(BodySchema)] = None

        class Response(Schema):
            group_id = fields.Integer()
            body = fields.Nested(BodySchema)

        async def execute(self, payload: Payload):
            from dataclasses import asdict
            return asdict(payload)

    request = mock.MagicMock(spec_set=Request)
    request.path_params = {'group_id': 1000}
    request.body.return_value = json.dumps({'name': 'Dataclass', 'email': 'email@mail.com'}).encode('utf8')

    user = await execute(TestMethod, request)
    assert user == {'body': {'name': 'Dataclass', 'email': 'email@mail.com'}, 'group_id': 1000}


async def execute(method, request, status_code: int = 200,
                  media_type='application/json') -> Mapping:
    endpoint = method.as_endpoint()
    resp = await endpoint(request)
    assert resp is not None
    assert isinstance(resp, Response)
    assert resp.status_code == status_code
    assert resp.media_type == media_type
    body = resp.body
    assert body is not None
    data = json.loads(body)
    return data
