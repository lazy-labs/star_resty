import types
from typing import Mapping, Type, TypeVar, Union

from marshmallow import EXCLUDE, Schema
from starlette.requests import Request

from .parser import Parser, set_parser

__all__ = ('path', 'path_schema', 'PathParser')

P = TypeVar('P')


def path_schema(schema: Union[Schema, Type[Schema]], cls: P,
                unknown=EXCLUDE) -> P:
    return types.new_class('PathInputParams', (cls,),
                           exec_body=set_parser(PathParser.create(schema, unknown=unknown)))


def path(schema: Union[Schema, Type[Schema]], unknown=EXCLUDE) -> Type[Mapping]:
    return path_schema(schema, Mapping, unknown=unknown)


class PathParser(Parser):
    __slots__ = ()

    @property
    def location(self):
        return 'path'

    def parse(self, request: Request):
        return self.schema.load(request.path_params, unknown=self.unknown)
