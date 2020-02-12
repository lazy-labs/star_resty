from typing import Sequence, Union

from apispec import APISpec
from starlette.routing import Route, Mount

from .operation import setup_route_operations
from .utils import convert_path

__all__ = ('setup_routes',)


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

        endpoint = getattr(route.endpoint, '__endpoint__', None)
        if endpoint is None:
            continue

        operations = setup_route_operations(route, endpoint, version=version,
                                            add_head_methods=add_head_methods)
        route_path = f'{path}{route.path}'
        spec.path(convert_path(route_path), operations=operations)
