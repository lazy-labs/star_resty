from starlette.routing import Route

from star_resty.method import Method
from .request import resolve_parameters, resolve_request_body, resolve_request_body_params
from .response import resolve_responses

__all__ = ('setup_route_operations',)


def setup_route_operations(route: Route, endpoint: Method, version: int = 2,
                           add_head_methods: bool = False):
    operation = setup_operation(endpoint, version=version)
    operation = {key: val for key, val in operation.items() if val is not None}
    return {method.lower(): operation for method in route.methods
            if (method != 'HEAD' or add_head_methods)}


def setup_operation(endpoint: Method, version=2):
    options = endpoint.meta
    res = {
        'tags': [options.tag],
        'description': options.description,
        'summary': options.summary,
        'produces': [endpoint.serializer.media_type],
        'parameters': resolve_parameters(endpoint),
        'responses': resolve_responses(endpoint),
    }

    if options.security is not None:
        res['security'] = options.security

    if version > 2:
        res['requestBody'] = resolve_request_body(endpoint)
    else:
        res['parameters'].extend(resolve_request_body_params(endpoint))

    if options.meta:
        res.update(options.meta)

    return res
