import types
from typing import Mapping, Type, TypeVar, Union

from marshmallow import EXCLUDE, Schema
from starlette.requests import Request

from .parser import Parser, set_parser

__all__ = ('json_schema', 'json_payload')

P = TypeVar('P')


def json_schema(schema: Union[Schema, Type[Schema]], cls: Type[P],
                unknown: str = EXCLUDE) -> P:
    return types.new_class('QueryInputParams', (cls,),
                           exec_body=set_parser(JsonParser.create(schema, unknown=unknown)))


def json_payload(schema: Union[Schema, Type[Schema]], unknown=EXCLUDE) -> Mapping:
    return json_schema(schema, Mapping, unknown=unknown)


class JsonParser(Parser):

    @property
    def location(self):
        return 'body'

    @property
    def media_type(self):
        return 'application/json'

    async def parse(self, request: Request):
        body = await request.json()
        if body is None:
            body = {}

        return self.schema.load(body, unknown=self.unknown)
