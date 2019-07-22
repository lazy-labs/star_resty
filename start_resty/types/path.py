import types
from typing import Mapping, Type, TypeVar, Union

from marshmallow import EXCLUDE, Schema
from starlette.requests import Request

from .parser import Parser

__all__ = ('path', 'path_schema')

P = TypeVar('P')


def path_schema(schema: Union[Schema, Type[Schema]], cls: P,
                unknown=EXCLUDE) -> P:
    def set_ns(ns):
        ns['parser'] = PathParser.create(schema, unknown=unknown)
        return ns

    return types.new_class('PathInputParams', (cls,), exec_body=set_ns)


def path(schema: Union[Schema, Type[Schema]], unknown=EXCLUDE) -> Type[Mapping]:
    return path_schema(schema, Mapping, unknown=unknown)


class PathParser(Parser):

    def parse(self, request: Request):
        return self.schema.load(request.path_params, unknown=self.unknown)
