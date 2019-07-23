from starlette.applications import Starlette
from starlette.testclient import TestClient

from start_resty.apidocs import setup_spec
from .utils.method import CreateUser


def test_generate_api_docs():
    app = Starlette()

    setup_spec(app, title='test')
    app.add_route('/users', CreateUser.as_endpoint(), methods=['POST'])

    client = TestClient(app)
    resp = client.get('/apidocs.json')
    assert resp is not None
    body = resp.json()
    assert body is not None
    assert body.get('info') == {'title': 'test', 'version': '0.0.1'}
    assert body.get('paths') == {
        '/users': {
            'post': {
                'parameters': [
                    {'format': 'int32', 'in': 'path', 'name': 'id', 'required': True, 'type': 'integer'},
                    {'in': 'body', 'name': 'body', 'required': False,
                     'schema': {'$ref': '#/definitions/tests.utils.method.BodySchema'}}],
                'produces': ['application/json'],
                'responses': {'201': {'schema': {
                    '$ref': '#/definitions/tests.utils.method.CreateUserResponse'}}},
                'tags': ['users'],
                'description': 'create user'
            }}}

    assert body.get('definitions') == {
        'tests.utils.method.BodySchema': {
            'properties': {'email': {'type': 'string'},
                           'name': {'type': 'string'}},
            'type': 'object'},
        'tests.utils.method.CreateUserResponse': {
            'properties': {'email': {'type': 'string'},
                           'id': {'format': 'int32',
                                  'type': 'integer'},
                           'name': {'type': 'string'}},
            'type': 'object'}}
