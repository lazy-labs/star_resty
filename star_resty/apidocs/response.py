import inspect
from typing import Union, Dict, Type

from star_resty.method import Method

__all__ = ('resolve_responses',)


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

    parser = getattr(endpoint, '__parser__', None)
    if parser and '404' not in responses:
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
