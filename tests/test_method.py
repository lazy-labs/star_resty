import json

import pytest
from asynctest import mock
from starlette.requests import Request
from starlette.responses import Response

from .utils.method import CreateUser


@pytest.mark.asyncio
async def test_create_user():
    request = mock.MagicMock(spec_set=Request)
    request.path_params = {'id': 1}
    request.json.return_value = {'name': 'Name', 'email': 'email@mail.com'}

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
