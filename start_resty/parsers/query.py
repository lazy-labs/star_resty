from functools import lru_cache
from typing import Callable, List, Mapping, Sequence

from marshmallow import EXCLUDE, Schema, fields
from starlette.requests import Request

__all__ = ('parse_query_params',)


def parse_query_params(request: Request, schema: Schema, unknown: str = EXCLUDE) -> Mapping:
    query_schema = get_query_schema(schema)
    query_params = request.query_params
    getlist = request.query_params.getlist
    data = ((key, query_schema[key](getlist(key)))
            for key in query_params.keys() if key in query_schema)
    data = {key: val for (key, val) in data if val is not None}

    return schema.load(data, many=False, unknown=unknown)


@lru_cache(1024)
def get_query_schema(schema: Schema) -> Mapping[str, Callable]:
    def iter_fields():
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

    return {key: val for (key, val) in iter_fields()}


def get_list_value(values: Sequence) -> List:
    return [v for v in values if v]


def get_value(values: Sequence):
    return next((v for v in values if v), None)
