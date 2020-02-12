import inspect
import types
from functools import lru_cache
from typing import Mapping, Type, TypeVar, Union, Callable, Sequence, List, Tuple, Iterator

from marshmallow import EXCLUDE, Schema, fields
from starlette.requests import Request

from .parser import Parser, set_parser

__all__ = ('query', 'query_schema', 'QueryParser')

Q = TypeVar('Q')


def query_schema(schema: Union[Schema, Type[Schema]], cls: Q,
                 unknown=EXCLUDE) -> Q:
    return types.new_class('QueryInputParams', (cls,),
                           exec_body=set_parser(QueryParser.create(schema, unknown=unknown)))


def query(schema: Union[Schema, Type[Schema]], unknown=EXCLUDE) -> Type[Mapping]:
    return query_schema(schema, Mapping, unknown=unknown)


class QueryParser(Parser):
    __slots__ = ('fields',)

    @classmethod
    def create(cls, schema: Union[Schema, Type[Schema]], unknown: str = EXCLUDE):
        schema, query_fields = get_query_fields(schema)
        return cls(schema, query_fields, unknown)

    def __init__(self, schema: Schema, query_fields: Mapping, unknown=EXCLUDE):
        super().__init__(schema, unknown=unknown)
        self.fields = query_fields

    @property
    def location(self):
        return 'query'

    def parse(self, request: Request):
        query_params = request.query_params
        getlist = request.query_params.getlist
        query_fields = self.fields
        data = ((key, query_fields[key](getlist(key)))
                for key in query_params.keys() if key in query_fields)
        data = {key: val for (key, val) in data if val is not None}
        return self.schema.load(data, many=False, unknown=self.unknown)


@lru_cache(typed=False, maxsize=1024)
def get_query_fields(schema: Union[Schema, Type[Schema]]) -> Tuple[Schema, Mapping[str, Callable]]:
    if inspect.isclass(schema):
        schema = schema()

    query_fields = dict(iter_query_fields(schema))
    return schema, query_fields


def iter_query_fields(schema: Schema) -> Iterator[Tuple[str, Callable]]:
    for key, field in schema.fields.items():
        field: fields.Field
        if field.dump_only or isinstance(field, fields.Constant):
            continue

        if field.attribute:
            name = field.attribute
        else:
            name = key

        if isinstance(field, fields.List):
            func = get_list_value
        else:
            func = get_value

        yield name, func
        if field.data_key:
            yield field.data_key, func


def get_list_value(values: Sequence) -> List:
    return [v for v in values if v]


def get_value(values: Sequence):
    return next((v for v in values if v), None)
