import logging
from typing import Optional, Mapping

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse

from .route import setup_routes
from .utils import resolve_schema_name, apispec_json_to_html

logger = logging.getLogger(__name__)

__all__ = ('setup_spec',)


def setup_spec(app: Starlette, title: str,
               version: str = '0.0.1',
               openapi_version='2.0',
               schemes=None,
               base_path='/',
               route: str = '/apidocs.json',
               route_html: str = '/apidocs',
               add_head_methods: bool = False,
               options: Optional[Mapping] = None,
               **kwargs):
    if options is None:
        options = {}

    spec = APISpec(
        title=title,
        version=version,
        openapi_version=openapi_version,
        schemes=schemes or ['http', 'https'],
        plugins=[MarshmallowPlugin(schema_name_resolver=resolve_schema_name)],
        **{'swagger': openapi_version, 'basePath': base_path, **options, **kwargs}
    )
    api_spec = None

    @app.route(route, include_in_schema=False)
    def generate_api_docs(_: Request):
        s = generate_spec(app, get_open_api_version(openapi_version), add_head_methods)
        return JSONResponse(s)

    @app.route(route_html, include_in_schema=False)
    def generate_html_api_docs(_: Request):
        s = generate_spec(app, get_open_api_version(openapi_version), add_head_methods)
        return HTMLResponse(apispec_json_to_html(s))

    def generate_spec(app: Starlette, open_api_version: int, add_head_methods: bool):
        nonlocal api_spec
        nonlocal spec
        if api_spec is None:
            logger.info('initialize open api schema')
            setup_routes(app.routes, spec, version=open_api_version, add_head_methods=add_head_methods)
            api_spec = spec.to_dict()
        return api_spec


def get_open_api_version(version: str) -> int:
    v = version.split('.', maxsplit=1)[0]
    try:
        return int(v)
    except (ValueError, TypeError):
        raise ValueError(f'Invalid open api version: {version}')
