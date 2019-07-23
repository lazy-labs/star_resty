import abc
import inspect
from functools import wraps
from typing import Any, Callable, ClassVar, Dict, List, Sequence, Tuple, Type, Union

from marshmallow import Schema
from starlette.requests import Request
from starlette.responses import Response

from start_resty.operation import Operation
from start_resty.serializers import JsonSerializer, Serializer
from .parser import Parser

__all__ = ('Method', 'endpoint', 'MethodMetaOptions', 'RequestParser')


class RequestParser:
    __slots__ = ('parsers', 'async_parsers')

    def __init__(self):
        self.parsers: List[Tuple[str, Parser]] = []
        self.async_parsers: List[Tuple[str, Parser]] = []

    def iter_parsers(self):
        yield from (p[1] for p in self.parsers)
        yield from (p[1] for p in self.async_parsers)

    async def parse(self, request: Request) -> Dict:
        params = {}
        for (key, p) in self.parsers:
            params[key] = p.parse(request)

        for (key, p) in self.async_parsers:
            params[key] = await p.parse(request)

        return params


class MethodMetaOptions:
    __slots__ = ('parser', 'render')

    def __init__(self, request_parser: RequestParser, render: Callable):
        self.parser = request_parser
        self.render = render


class MethodMeta(abc.ABCMeta):

    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs, **kwargs)

        func = getattr(cls, 'execute', None)
        meta = MethodMetaOptions(request_parser=mcs.create_parser(func),
                                 render=mcs.create_render(cls))
        cls.__meta__ = meta
        return cls

    @classmethod
    def create_render(mcs, method):
        renders = []
        response_schema = getattr(method, 'response_schema', None)
        if response_schema is not None:
            if inspect.isclass(response_schema):
                response_schema = response_schema()

            renders.append(response_schema.dump)

        if method.serializer is not None:
            renders.append(mcs.render_bytes(method.serializer, method.status_code or 200))

        return mcs.create_content_render(tuple(renders))

    @staticmethod
    def create_content_render(renders: Tuple) -> Callable:
        def render(content: Any):
            for r in renders:
                content = r(content)

            return content

        return render

    @staticmethod
    def create_parser(func):
        req_parser = RequestParser()
        if func is None:
            return req_parser

        data = func.__annotations__
        for key, value in data.items():
            parser = getattr(value, 'parser', None)
            if parser is None or not isinstance(parser, Parser):
                continue

            if inspect.iscoroutinefunction(parser.parse):
                req_parser.async_parsers.append((key, parser))
            else:
                req_parser.parsers.append((key, parser))

        return req_parser

    @staticmethod
    def render_bytes(serializer, status_code):
        def render(content):
            return Response(serializer.render(content),
                            media_type=serializer.media_type,
                            status_code=status_code)

        return render


class Method(abc.ABC, metaclass=MethodMeta):
    __slots__ = ('request',)
    __meta__: ClassVar[MethodMetaOptions]

    meta: ClassVar[Operation] = Operation(tag='default')
    serializer: ClassVar[Serializer] = JsonSerializer
    response_schema: ClassVar[Union[Schema, Type[Schema], None]] = None
    status_code: int = 200
    errors: ClassVar[Sequence] = ()

    def __init__(self, request: Request):
        self.request = request

    @abc.abstractmethod
    async def execute(self, *args, **kwargs):
        pass

    async def dispatch(self) -> Response:
        meta = self.__meta__
        params = await meta.parser.parse(self.request)
        content = await self.execute(**params)
        return meta.render(content)

    @classmethod
    def as_endpoint(cls):
        return endpoint(cls)


def endpoint(cls: Type[Method]):
    @wraps(cls)
    async def wrapper(request: Request) -> Response:
        method = cls(request)
        return await method.dispatch()

    wrapper.__endpoint__ = cls
    return wrapper
