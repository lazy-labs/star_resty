import abc
import inspect
from functools import lru_cache
from typing import Dict, Optional, Type, Union, Iterable, Mapping, Tuple

from marshmallow import EXCLUDE, Schema
from starlette.requests import Request

__all__ = ('Parser', 'SchemaParser', 'set_parser')


class Parser(abc.ABC):
    __slots__ = ()

    @abc.abstractmethod
    def parse(self, request: Request):
        raise NotImplementedError

    @staticmethod
    def get_spec() -> Iterable[Mapping]:
        return ()

    @staticmethod
    def get_body_spec() -> Iterable[Tuple[str, Mapping]]:
        return ()

    @property
    def location(self) -> Optional[str]:
        return None

    @property
    def media_type(self) -> Optional[str]:
        return None

    @property
    def is_body(self) -> bool:
        return self.location == 'body'



class SchemaParser(Parser, metaclass=abc.ABCMeta):
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

    def get_spec(self):
        yield {'in': self.location, 'schema': self.schema}

    def get_body_spec(self):
        if self.media_type:
            yield self.media_type, {'schema': self.schema}


def set_parser(parser: Parser):
    def handler(ns: Dict):
        ns['parser'] = parser
        return ns

    return handler
