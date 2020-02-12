import types
from typing import Mapping, Type, TypeVar, Union

import ujson
from marshmallow import EXCLUDE, Schema
from starlette.requests import Request

from star_resty.exceptions import DecodeError
from .parser import Parser, set_parser

__all__ = ('json_schema', 'json_payload', 'JsonParser')

P = TypeVar('P')


def json_schema(schema: Union[Schema, Type[Schema]], cls: P,
                unknown: str = EXCLUDE) -> P:
    return types.new_class('JsonInputParams', (cls,),
                           exec_body=set_parser(JsonParser.create(schema, unknown=unknown)))


def json_payload(schema: Union[Schema, Type[Schema]], unknown=EXCLUDE) -> Type[Mapping]:
    return json_schema(schema, Mapping, unknown=unknown)


class JsonParser(Parser):
    __slots__ = ()

    @property
    def location(self):
        return 'body'

    @property
    def media_type(self):
        return 'application/json'

    async def parse(self, request: Request):
        body = await request.body()
        if body is None:
            data = {}
        else:
            try:
                data = ujson.loads(body)
            except (TypeError, ValueError) as e:
                raise DecodeError('Invalid json body') from e

        return self.schema.load(data, unknown=self.unknown)
