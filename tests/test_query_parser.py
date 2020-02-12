from unittest.mock import MagicMock

import pytest
from marshmallow import Schema, ValidationError, fields
from starlette.datastructures import QueryParams
from starlette.requests import Request

from star_resty.payload.query import QueryParser


class QuerySchema(Schema):
    limit = fields.Integer(required=True)
    item_id = fields.List(fields.Integer())
    a = fields.String(data_key='b')
    n = fields.Constant(1)


def test_parse_query_args_raise_validation_error():
    request = MagicMock(spec=Request)
    request.query_params = QueryParams([('item_id', '1'), ('item_id', '2')])
    parser = QueryParser.create(QuerySchema)
    with pytest.raises(ValidationError):
        parser.parse(request)


def test_parse_query_args():
    request = MagicMock(spec=Request)
    request.query_params = QueryParams([
        ('item_id', '1'), ('item_id', '2'), ('limit', '1000'),
        ('b', '2'), ('n', '100')])
    parser = QueryParser.create(QuerySchema)
    params = parser.parse(request)
    assert params == {'limit': 1000, 'item_id': [1, 2], 'a': '2', 'n': 1}
