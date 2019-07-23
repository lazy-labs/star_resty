from marshmallow import Schema, fields

from start_resty import Operation
from start_resty.types import Method, json_payload, path


class PathParams(Schema):
    id = fields.Integer(required=True)


class BodySchema(Schema):
    name = fields.String()
    email = fields.String()


class CreateUserResponse(Schema):
    id = fields.Integer()
    name = fields.String()
    email = fields.String()


class CreateUser(Method):
    meta = Operation(tag='users', description='create user')
    response_schema = CreateUserResponse
    status_code = 201

    async def execute(self, user: path(PathParams),
                      payload: json_payload(BodySchema)):
        return {'id': user['id'], **payload}
