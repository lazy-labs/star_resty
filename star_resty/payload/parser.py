import abc
import inspect
from typing import Dict, Optional, Type, Union
from apispec import APISpec

from marshmallow import EXCLUDE, Schema
from starlette.requests import Request
from functools import lru_cache

__all__ = ('Parser', 'set_parser')


class Parser(abc.ABC):
    __slots__ = ('schema', 'unknown')

    @classmethod
    def create(cls, schema: Union[Schema, Type[Schema]], unknown: str = EXCLUDE):
        return cls(cls._convert_schema(schema), unknown)

    @staticmethod
    @lru_cache(maxsize=1024)
    def _convert_schema(schema: Union[Schema, Type[Schema]]) -> Schema:
        if inspect.isclass(schema):
            if not issubclass(schema, Schema):
                raise TypeError(f'Invalid schema type: {schema}')

            return schema()
        elif not isinstance(schema, Schema):
            raise TypeError(f'Invalid schema type: {type(schema)}')

        return schema

    def __init__(self, schema: Schema, unknown=EXCLUDE):
        self.schema = schema
        self.unknown = unknown

    @abc.abstractmethod
    def parse(self, request: Request):
        pass

    def get_spec(self, spec: APISpec = None) -> Dict[str, Union[str, Dict]]:
        return {'in': self.location, 'schema': self.schema}

    @property
    def in_body(self) -> bool:
        return self.location == 'body'

    @property
    def location(self) -> Optional[str]:
        return None

    @property
    def media_type(self) -> Optional[str]:
        return None


def set_parser(parser: Parser):
    def handler(ns: Dict):
        ns['parser'] = parser
        return ns

    return handler
