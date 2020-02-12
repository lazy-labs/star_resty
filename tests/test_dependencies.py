import inspect
from dataclasses import dataclass
from typing import Mapping

from marshmallow import EXCLUDE, Schema, fields

from star_resty.payload import (json_payload, json_schema, path, path_schema, query, query_schema)


class QuerySchema(Schema):
    q = fields.String()
    limit = fields.Integer()
    offset = fields.Integer()


class UserSchema(Schema):
    id = fields.Integer(required=True)


@dataclass
class User:
    id: int


@dataclass
class QueryParams:
    q: str
    limit: int = 100
    offset: int = 0


def test_query_schema_dependency():
    query_dep = query_schema(QuerySchema, QueryParams, unknown=EXCLUDE)
    assert query_dep is not None
    assert inspect.isclass(query_dep)
    assert issubclass(query_dep, QueryParams)
    parser = getattr(query_dep, 'parser', None)
    assert parser is not None
    assert parser.location == 'query'
    assert isinstance(parser.schema, QuerySchema)


def test_query_dependency():
    query_dep = query(QuerySchema, unknown=EXCLUDE)
    assert query_dep is not None
    assert inspect.isclass(query_dep)
    assert issubclass(query_dep, Mapping)
    parser = getattr(query_dep, 'parser', None)
    assert parser is not None
    assert parser.location == 'query'
    assert isinstance(parser.schema, QuerySchema)


def test_path_schema_dependency():
    path_dep = path_schema(UserSchema, User, unknown=EXCLUDE)
    assert path_dep is not None
    assert inspect.isclass(path_dep)
    assert issubclass(path_dep, User)
    parser = getattr(path_dep, 'parser', None)
    assert parser is not None
    assert parser.location == 'path'
    assert isinstance(parser.schema, UserSchema)


def test_path_dependency():
    path_dep = path(UserSchema, unknown=EXCLUDE)
    assert path_dep is not None
    assert inspect.isclass(path_dep)
    assert issubclass(path_dep, Mapping)
    parser = getattr(path_dep, 'parser', None)
    assert parser is not None
    assert parser.location == 'path'
    assert isinstance(parser.schema, UserSchema)


def test_json_body_schema_dependency():
    json_dep = json_schema(QuerySchema, User, unknown=EXCLUDE)
    assert json_dep is not None
    assert inspect.isclass(json_dep)
    assert issubclass(json_dep, User)
    parser = getattr(json_dep, 'parser', None)
    assert parser is not None
    assert parser.location == 'body'
    assert isinstance(parser.schema, QuerySchema)


def test_json_body_dependency():
    json_dep = json_payload(QuerySchema, unknown=EXCLUDE)
    assert json_dep is not None
    assert inspect.isclass(json_dep)
    assert issubclass(json_dep, Mapping)
    parser = getattr(json_dep, 'parser', None)
    assert parser is not None
    assert parser.location == 'body'
    assert isinstance(parser.schema, QuerySchema)
