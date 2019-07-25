import inspect
import re
from typing import Any

__all__ = ('resolve_schema_name', 'convert_path')


def resolve_schema_name(schema: Any) -> str:
    if inspect.isclass(schema):
        cls = schema
    else:
        cls = schema.__class__

    name = f'{cls.__module__}.{cls.__qualname__}'
    return name


def convert_path(path: str) -> str:
    return re.sub(r'{([^:]+).*}', r'{\1}', path)
