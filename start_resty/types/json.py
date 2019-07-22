import types
from typing import Mapping, Type, TypeVar, Union

from marshmallow import EXCLUDE, Schema
from starlette.requests import Request

from .parser import Parser

__all__ = ('json_schema', 'json_payload')

P = TypeVar('P')


def json_schema(schema: Union[Schema, Type[Schema]], cls: P,
                unknown: str = EXCLUDE) -> P:
    def set_ns(ns):
        ns['parser'] = JsonParser.create(schema, unknown=unknown)
        return ns

    return types.new_class('QueryInputParams', (cls,), exec_body=set_ns)


def json_payload(schema: Union[Schema, Type[Schema]], unknown=EXCLUDE) -> Type[Mapping]:
    return json_schema(schema, Mapping, unknown=unknown)


class JsonParser(Parser):

    async def parse(self, request: Request):
        body = await request.json()
        if body is None:
            body = {}

        return self.schema.load(body, unknown=self.unknown)
