from apispec import APISpec
from star_resty.method import Method
from star_resty.method.parser import RequestParser

__all__ = ('resolve_parameters', 'resolve_request_body', 'resolve_request_body_params')


def resolve_parameters(endpoint: Method, spec: APISpec):
    parameters = []
    parser = getattr(endpoint, '__parser__', None)
    if parser is None:
        return parameters

    for p in parser:
        if p.schema is not None and not p.in_body:
            parameters.append(p.get_spec(spec=spec))

    return parameters


def resolve_request_body(endpoint: Method):
    parser = getattr(endpoint, '__parser__', None)
    if parser is None:
        return None

    content = resolve_request_body_content(parser)
    if content:
        return {'content': content}


def resolve_request_body_content(parser: RequestParser):
    content = {}
    for p in parser:
        if p.schema is not None and p.in_body and p.media_type:
            content[p.media_type] = {'schema': p.schema}

    return content


def resolve_request_body_params(endpoint: Method):
    params = []
    parser = getattr(endpoint, '__parser__', None)
    if parser is None:
        return params

    for p in parser:
        if p.schema is not None and p.location == 'body' and p.media_type:
            params.append({
                'name': 'body',
                'in': 'body',
                'schema': p.schema
            })

    return params
