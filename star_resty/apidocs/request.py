from star_resty.method import Method
from star_resty.method.parser import RequestParser

__all__ = ('resolve_parameters', 'resolve_request_body', 'resolve_request_body_params')


def resolve_parameters(endpoint: Method):
    parameters = []
    parser = getattr(endpoint, '__parser__', None)
    if parser is None:
        return parameters

    for p in parser:
        if not p.is_body:
            parameters.extend(p.get_spec())

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
        if p.is_body:
            content.update(p.get_body_spec())

    return content


def resolve_request_body_params(endpoint: Method):
    params = []
    parser = getattr(endpoint, '__parser__', None)
    if parser is None:
        return params

    for p in parser:
        if p.is_body:
            params.extend(p.get_spec())

    return params
