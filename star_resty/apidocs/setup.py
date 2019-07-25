import inspect
import logging
from typing import Dict, Optional, Sequence, Type, Union

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import UJSONResponse
from starlette.routing import Mount, Route

from star_resty.method import Method
from star_resty.method.meta import MethodMetaOptions
from star_resty.method.request_parser import RequestParser
from .utils import convert_path, resolve_schema_name

logger = logging.getLogger(__name__)

__all__ = ('setup_spec',)


def setup_spec(app: Starlette, title: str,
               version: str = '0.0.1',
               openapi_version='2.0',
               schemes=None,
               base_path='/',
               route: str = '/apidocs.json',
               add_head_methods: bool = False,
               **kwargs):
    spec = APISpec(
        title=title,
        version=version,
        openapi_version=openapi_version,
        schemes=schemes or ['http', 'https'],
        plugins=[MarshmallowPlugin(schema_name_resolver=resolve_schema_name)],
        **{**kwargs, 'swagger': '2.0', 'basePath': base_path}
    )
    initialized = False

    @app.route(route, include_in_schema=False)
    def generate_api_docs(_: Request):
        nonlocal initialized
        nonlocal spec
        if not initialized:
            logger.info('initialize open api schema')
            setup_paths(app, spec,
                        version=get_open_api_version(openapi_version),
                        add_head_methods=add_head_methods)
            initialized = True

        return UJSONResponse(spec.to_dict())


def get_open_api_version(version: str) -> int:
    v = version.split('.', maxsplit=1)[0]
    try:
        return int(v)
    except (ValueError, TypeError):
        raise ValueError(f'Invalid open api version: {version}')


def setup_paths(app: Starlette, spec: APISpec, version: int = 2,
                add_head_methods: bool = False):
    setup_routes(app.routes, spec, version, add_head_methods)


def setup_routes(routes: Sequence[Union[Route, Mount]],
                 spec: APISpec, version: int = 2,
                 add_head_methods: bool = False,
                 path: str = ''):
    for route in routes:
        if isinstance(route, Mount):
            setup_routes(route.routes, spec, version=version, add_head_methods=add_head_methods,
                         path=f'{path}{route.path}')
            continue
        elif isinstance(route, Route) and not route.include_in_schema:
            continue

        endpoint: Optional[Method] = getattr(route.endpoint, '__endpoint__', None)
        if endpoint is None:
            continue

        operations = setup_operations(route, endpoint, version=version,
                                      add_head_methods=add_head_methods)
        route_path = f'{path}{route.path}'
        spec.path(convert_path(route_path), operations=operations)


def setup_operations(route: Route, endpoint: Method, version: int = 2,
                     add_head_methods: bool = False):
    operation = setup_operation(endpoint, version=version)
    operation = {key: val for key, val in operation.items() if val is not None}
    return {method.lower(): operation for method in route.methods
            if (method != 'HEAD' or add_head_methods)}


def setup_operation(endpoint: Method, version=2):
    options = endpoint.meta
    meta = endpoint.__meta__
    res = {
        'tags': [options.tag],
        'description': options.description,
        'summary': options.summary,
        'produces': [endpoint.serializer.media_type],
        'parameters': resolve_parameters(meta),
        'responses': resolve_responses(endpoint)
    }
    if version > 2:
        res['requestBody'] = resolve_request_body(meta)
    else:
        res['parameters'].extend(resolve_request_body_params(meta.parser))

    return res


def resolve_parameters(meta: MethodMetaOptions):
    parameters = []
    parser = meta.parser
    if parser is None:
        return parameters

    for p in parser.iter_parsers():
        if p.schema is not None and p.location != 'body':
            parameters.append({'in': p.location, 'schema': p.schema})

    return parameters


def resolve_request_body(meta: MethodMetaOptions):
    parser = meta.parser
    if parser is None:
        return None

    content = resolve_request_body_content(parser)
    if content:
        return {'content': content}


def resolve_request_body_content(parser: RequestParser):
    content = {}
    for p in parser.iter_parsers():
        if p.schema is not None and p.location == 'body' and p.media_type:
            content[p.media_type] = {'schema': p.schema}

    return content


def resolve_request_body_params(parser: RequestParser):
    params = []
    for p in parser.iter_parsers():
        if p.schema is not None and p.location == 'body' and p.media_type:
            params.append({
                'name': 'body',
                'in': 'body',
                'schema': p.schema
            })

    return params


def resolve_responses(endpoint: Method):
    responses = {}
    if endpoint.response_schema:
        responses[str(endpoint.status_code)] = {
            'schema': endpoint.response_schema
        }

    errors = endpoint.meta.errors or ()
    for e in errors:
        if isinstance(e, dict) and e.get('status_code'):
            responses[str(e['status_code'])] = {key: val for key, val in e.items() if key != 'status_code'}
        elif isinstance(e, Exception) and getattr(e, 'status_code', None) is not None:
            responses[str(getattr(e, 'status_code'))] = create_error_schema_by_exc(e)
        elif inspect.isclass(e) and issubclass(e, Exception) and getattr(e, 'status_code', None) is not None:
            responses[str(getattr(e, 'status_code'))] = create_error_schema_by_exc(e)

    if not endpoint.__meta__.parser.is_empty and '404' not in responses:
        responses['400'] = {'description': 'Bad request'}

    return responses


def create_error_schema_by_exc(e: Union[Exception, Type[Exception]]) -> Dict:
    schema = {'description': (getattr(e, 'detail', None)
                              or getattr(e, 'description', None)
                              or str(e))}
    error_schema = getattr(e, 'schema', None)
    if error_schema is not None:
        schema['schema'] = error_schema

    return schema
