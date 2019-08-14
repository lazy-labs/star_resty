import types
from typing import Mapping, Type, TypeVar, Union

from marshmallow import EXCLUDE, Schema
from starlette.requests import Request

from star_resty.parsers import parse_query_params
from .parser import Parser, set_parser

__all__ = ('query', 'query_schema')

Q = TypeVar('Q')


def query_schema(schema: Union[Schema, Type[Schema]], cls: Type[Q],
                 unknown=EXCLUDE) -> Q:
    return types.new_class('QueryInputParams', (cls,),
                           exec_body=set_parser(QueryParser.create(schema, unknown=unknown)))


def query(schema: Union[Schema, Type[Schema]], unknown=EXCLUDE) -> Mapping:
    return query_schema(schema, Mapping, unknown=unknown)


class QueryParser(Parser):

    @property
    def location(self):
        return 'query'

    def parse(self, request: Request):
        return parse_query_params(request, self.schema, unknown=self.unknown)
