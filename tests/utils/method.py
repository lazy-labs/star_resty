from marshmallow import Schema, fields

from star_resty import Operation
from star_resty.types import Method, json_payload, path, query


class PathParams(Schema):
    id = fields.Integer(required=True)


class BodySchema(Schema):
    name = fields.String()
    email = fields.String()


class QueryParams(Schema):
    q = fields.String()


class CreateUserResponse(Schema):
    id = fields.Integer()
    name = fields.String()
    email = fields.String()


class SearchUserResponse(Schema):
    id = fields.Int()
    q = fields.String()


class CreateUser(Method):
    meta = Operation(tag='users', description='create user')
    response_schema = CreateUserResponse
    status_code = 201

    async def execute(self, user: path(PathParams),
                      payload: json_payload(BodySchema)):
        return {'id': user['id'], **payload}


class SearchUser(Method):
    mata = Operation(tag='users', description='search user')
    response_schema = SearchUserResponse
    status_code = 200

    async def execute(self, user: path(PathParams), query_params: query(QueryParams)):
        return {**user, **query_params}
