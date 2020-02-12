import types
from typing import Mapping, Type, TypeVar, Union

from marshmallow import EXCLUDE, Schema
from starlette.requests import Request

from .parser import Parser, set_parser

__all__ = ('header', 'header_schema', 'HeaderParser')

P = TypeVar('P')


def header_schema(schema: Union[Schema, Type[Schema]], cls: P,
                  unknown=EXCLUDE) -> P:
    return types.new_class('HeaderInputParams', (cls,),
                           exec_body=set_parser(HeaderParser.create(schema, unknown=unknown)))


def header(schema: Union[Schema, Type[Schema]], unknown=EXCLUDE) -> Type[Mapping]:
    return header_schema(schema, Mapping, unknown=unknown)


class HeaderParser(Parser):
    __slots__ = ()

    @property
    def location(self):
        return 'header'

    def parse(self, request: Request):
        return self.schema.load(request.headers, unknown=self.unknown)
