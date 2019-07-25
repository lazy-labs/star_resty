from marshmallow import ValidationError
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from tests.utils.method import SearchUser, GetItemsEcho


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

    @app.exception_handler(ValidationError)
    async def error(request, exc: ValidationError):
        return JSONResponse({'success': False, 'errors': exc.normalized_messages()},
                            status_code=400)

    client = TestClient(app)
    resp = client.get('/users/invalid?q=Test')
    assert resp.status_code == 400


def test_nested_result():
    app = Starlette()

    app.add_route('/items', GetItemsEcho.as_endpoint(), methods=['GET'])
    client = TestClient(app)
    resp = client.get('/items?id=1&id=2&id=3')
    assert resp.status_code == 200
    data = resp.json()
    assert data == {'items': [{'id': 1}, {'id': 2}, {'id': 3}]}
