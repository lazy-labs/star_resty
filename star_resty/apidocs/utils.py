import inspect
import os
import re
import json
from typing import Any

__all__ = ('resolve_schema_name', 'convert_path', 'apispec_json_to_html')


def resolve_schema_name(schema: Any) -> str:
    if inspect.isclass(schema):
        cls = schema
    else:
        cls = schema.__class__

    name = f'{cls.__module__}.{cls.__qualname__}'
    return name


def convert_path(path: str) -> str:
    return re.sub(r'{([^:]+).*}', r'{\1}', path)


def apispec_json_to_html(apispec_json: dict) -> str:
    template_path = os.path.join(os.path.dirname(__file__), 'template.html')
    with open(template_path, 'r') as file:
        template = file.read()
    return template % json.dumps(apispec_json)
