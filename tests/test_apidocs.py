from starlette.applications import Starlette
from starlette.routing import Mount, Route, Router
from starlette.testclient import TestClient

from star_resty.apidocs import setup_spec
from .utils.method import CreateUser, GetUser, SearchUser, GetItemsEcho


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
                'responses': {
                    '201': {'schema': {
                        '$ref': '#/definitions/tests.utils.method.CreateUserResponse'}},
                    '400': {'description': 'Bad request'}},
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


def test_generate_api_docs_for_router():
    routes = [
        Mount('/v1', Router([
            Route('/users', CreateUser.as_endpoint(), methods=['POST']),
            Route('/users', SearchUser.as_endpoint(), methods=['GET'])
        ]))
    ]
    app = Starlette(routes=routes)

    setup_spec(app, title='test')

    client = TestClient(app)
    resp = client.get('/apidocs.json')
    assert resp is not None
    body = resp.json()
    assert body is not None
    assert body.get('paths') == {
        '/v1/users': {
            'post': {'tags': ['users'], 'description': 'create user', 'produces': ['application/json'],
                     'parameters': [
                         {'in': 'path', 'name': 'id', 'required': True, 'type': 'integer', 'format': 'int32'},
                         {'in': 'body', 'required': False, 'name': 'body',
                          'schema': {'$ref': '#/definitions/tests.utils.method.BodySchema'}}],
                     'responses': {
                         '201': {'schema': {'$ref': '#/definitions/tests.utils.method.CreateUserResponse'}},
                         '400': {'description': 'Bad request'}}},
            'get': {'tags': ['default'], 'produces': ['application/json'],
                    'parameters': [
                        {'in': 'path', 'name': 'id', 'required': True, 'type': 'integer', 'format': 'int32'},
                        {'in': 'query', 'name': 'q', 'required': False, 'type': 'string'}],
                    'responses': {
                        '200': {'schema': {'$ref': '#/definitions/tests.utils.method.SearchUserResponse'}},
                        '400': {'description': 'Bad request'}}}}}


def test_generate_api_docs_for_path():
    app = Starlette()

    setup_spec(app, title='test')
    app.add_route('/users/{user_id:int}', GetUser.as_endpoint(), methods=['POST'])

    client = TestClient(app)
    resp = client.get('/apidocs.json')
    assert resp is not None
    body = resp.json()
    assert body is not None
    assert body.get('paths') == {
        '/users/{user_id}': {
            'post': {
                'tags': ['users'], 'description': 'get user', 'produces': ['application/json'],
                'parameters': [
                    {'in': 'path', 'name': 'id', 'required': True, 'type': 'integer', 'format': 'int32'},
                    {'in': 'body', 'required': False, 'name': 'body',
                     'schema': {'$ref': '#/definitions/tests.utils.method.BodySchema'}}],
                'responses': {
                    '200': {'schema': {'$ref': '#/definitions/tests.utils.method.CreateUserResponse'}},
                    '400': {'description': 'Bad request'}}}}}


def test_generate_api_docs_for_nested():
    app = Starlette()

    setup_spec(app, title='test')
    app.add_route('/items', GetItemsEcho.as_endpoint(), methods=['GET'])

    client = TestClient(app)
    resp = client.get('/apidocs.json')
    assert resp is not None
    body = resp.json()
    assert body is not None
    assert body.get('paths') == {
        '/items': {
            'get': {'tags': ['items'], 'description': 'get items', 'produces': ['application/json'], 'parameters': [
                {'in': 'query', 'name': 'id', 'required': False, 'collectionFormat': 'multi', 'type': 'array',
                 'items': {'type': 'integer', 'format': 'int32'}}],
                    'responses': {'200': {'schema': {'$ref': '#/definitions/tests.utils.method.ItemsModel'}},
                                  '400': {'description': 'Bad request'}}}
        }
    }
