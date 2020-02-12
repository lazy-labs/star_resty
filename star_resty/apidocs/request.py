from star_resty.method import Method
from star_resty.method.parser import RequestParser

__all__ = ('resolve_parameters', 'resolve_request_body', 'resolve_request_body_params')


def resolve_parameters(endpoint: Method):
    parameters = []
    parser = getattr(endpoint, '__parser__', None)
    if parser is None:
        return parameters

    for p in parser:
        if p.schema is not None and p.location != 'body':
            parameters.append({'in': p.location, 'schema': p.schema})

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
        if p.schema is not None and p.location == 'body' and p.media_type:
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
