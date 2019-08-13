import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from star_resty import Method, inject
from tests.utils.method import SearchUserResponse


class Repository:

    @staticmethod
    async def get_user():
        return {'id': 2}


class GetUser(Method):
    response_schema = SearchUserResponse

    users_repository = inject.attr(Repository)

    async def execute(self):
        return await self.users_repository.get_user()


class GetUserInjByName(Method):
    response_schema = SearchUserResponse

    users_repository = inject.attr(Repository, name='user_api')

    async def execute(self):
        return await self.users_repository.get_user()


@pytest.fixture()
def app():
    return Starlette()


def test_inject_attr(app):
    app.users_repository = Repository()
    app.add_route('/user', GetUser.as_endpoint(), methods=['GET'])

    client = TestClient(app)
    resp = client.get('/user')
    assert resp.status_code == 200
    body = resp.json()
    assert body == {'id': 2}


def test_inject_attr_by_name(app):
    app.user_api = Repository()
    app.add_route('/user', GetUserInjByName.as_endpoint(), methods=['GET'])

    client = TestClient(app)
    resp = client.get('/user')
    assert resp.status_code == 200
    body = resp.json()
    assert body == {'id': 2}
