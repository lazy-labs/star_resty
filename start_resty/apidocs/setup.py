import re
from typing import Optional, Sequence

from apispec import APISpec
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import UJSONResponse
from starlette.routing import Route

from start_resty.types import Method


def setup_spec(app: Starlette, title: str,
               version: str = '0.0.1',
               openapi_version='3.0.2',
               schemes=None,
               base_path='/',
               **kwargs):
    spec = APISpec(
        title=title,
        version=version,
        openapi_version=openapi_version,
        schemes=schemes or ['http', 'https'],
        **{**kwargs, 'swagger': '2.0', 'basePath': base_path}
    )

    initialized = False

    @app.route('/apidocs.json', include_in_schema=False)
    def generate_api_docs(request: Request):
        nonlocal initialized
        nonlocal spec
        if not initialized:
            setup_paths(app, spec)
            initialized = True

        return UJSONResponse(spec.to_dict())


def setup_paths(app: Starlette, spec: APISpec):
    routes: Sequence[Route] = app.routes
    for route in routes:
        if not route.include_in_schema:
            continue

        endpoint: Optional[Method] = getattr(route.endpoint, '__endpoint__', None)
        if endpoint is None:
            continue

        operations = setup_operations(route, endpoint)
        spec.path(convert_path(route.path), operations=operations)


def setup_operations(route: Route, endpoint: Method):
    operation = setup_operation(endpoint)
    operation = {key: val for key, val in operation.items() if val is not None}
    return {method.lower(): operation for method in route.methods}


def setup_operation(endpoint: Method):
    meta = endpoint.meta
    res = {
        'tags': [meta.tag],
        'description': meta.description,
        'summary': meta.summary,
        'produces': [endpoint.serializer.media_type]
    }
    return res


def convert_path(path: str) -> str:
    return re.sub(r'<([^>]+)>', r'{\1}', path)
