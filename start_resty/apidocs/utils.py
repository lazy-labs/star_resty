import inspect
from typing import Any

__all__ = ('resolve_schema_name',)


def resolve_schema_name(schema: Any) -> str:
    if inspect.isclass(schema):
        cls = schema
    else:
        cls = schema.__class__

    name = f'{cls.__module__}.{cls.__qualname__}'
    return name
