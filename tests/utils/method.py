from marshmallow import Schema, fields

from star_resty import Method, Operation, json_payload, path, query


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


class ItemsModel(Schema):
    class Item(Schema):
        id = fields.Integer()

    items = fields.List(fields.Nested(Item))
    success = fields.Bool(missing=True)


class GetItemsEcho(Method):
    class Input(Schema):
        id = fields.List(fields.Integer())

    meta = Operation(tag='items', description='get items')
    response_schema = ItemsModel

    async def execute(self, items: query(Input)):
        return {'items': [{'id': item_id} for item_id in items['id']]}


class CreateUser(Method):
    meta = Operation(tag='users', description='create user')
    response_schema = CreateUserResponse
    status_code = 201

    async def execute(self, user: path(PathParams),
                      payload: json_payload(BodySchema)):
        return {'id': user['id'], **payload}


class GetUser(Method):
    meta = Operation(tag='users', description='get user')

    class Response(CreateUserResponse):
        pass

    async def execute(self, user: path(PathParams),
                      payload: json_payload(BodySchema)):
        return {'id': 1}


class SearchUser(Method):
    mata = Operation(tag='users', description='search user')
    response_schema = SearchUserResponse
    status_code = 200

    async def execute(self, user: path(PathParams), query_params: query(QueryParams)):
        return {**user, **query_params}
