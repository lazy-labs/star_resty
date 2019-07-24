from unittest.mock import MagicMock

import pytest
from marshmallow import Schema, ValidationError, fields
from starlette.datastructures import QueryParams
from starlette.requests import Request

from star_resty.parsers.query import parse_query_params


class QuerySchema(Schema):
    limit = fields.Integer(required=True)
    item_id = fields.List(fields.Integer())
    a = fields.String(data_key='b')
    n = fields.Constant(1)


def test_parse_query_args_raise_validation_error():
    request = MagicMock(spec=Request)
    request.query_params = QueryParams([('item_id', '1'), ('item_id', '2')])
    with pytest.raises(ValidationError):
        parse_query_params(request, QuerySchema())


def test_parse_query_args():
    request = MagicMock(spec=Request)
    request.query_params = QueryParams([
        ('item_id', '1'), ('item_id', '2'), ('limit', '1000'),
        ('b', '2'), ('n', '100')])
    params = parse_query_params(request, QuerySchema())
    assert params == {'limit': 1000, 'item_id': [1, 2], 'a': '2', 'n': 1}
