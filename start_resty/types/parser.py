import abc
import inspect
from typing import Type, Union

from marshmallow import EXCLUDE, Schema
from starlette.requests import Request

__all__ = ('Parser',)


class Parser(abc.ABC):
    __slots__ = ('schema', 'unknown')

    @classmethod
    def create(cls, schema: Union[Schema, Type[Schema]], unknown: str = EXCLUDE):
        if inspect.isclass(schema):
            if not issubclass(schema, Schema):
                raise TypeError(f'Invalid schema type: {schema}')

            schema = schema()
        elif not isinstance(schema, Schema):
            raise TypeError(f'Invalid schema type: {type(schema)}')

        return cls(schema, unknown)

    def __init__(self, schema: Schema, unknown=EXCLUDE):
        self.schema = schema
        self.unknown = unknown

    @abc.abstractmethod
    def parse(self, request: Request):
        pass
