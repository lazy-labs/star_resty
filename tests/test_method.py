import json

import pytest
from asynctest import mock
from marshmallow import ValidationError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.testclient import TestClient

from .utils.method import CreateUser, SearchUser


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


def test_search_user():
    app = Starlette()

    app.add_route('/users/{id}', SearchUser.as_endpoint(), methods=['GET'])

    client = TestClient(app)
    resp = client.get('/users/1?q=Test')
    assert resp.status_code == 200
    body = resp.json()
    assert body == {'id': 1, 'q': 'Test'}


def test_search_user_invalid_args():
    app = Starlette()

    app.add_route('/users/{id}', SearchUser.as_endpoint(), methods=['GET'])

    def register_error_handler(app: Starlette):
        @app.exception_handler(ValidationError)
        async def error(request, exc: ValidationError):
            return JSONResponse({'success': False, 'result': {'message': exc.messages}}, status_code=400)

    register_error_handler(app)

    client = TestClient(app)
    resp = client.get('/users/invalid?q=Test')
    assert resp.status_code == 400
