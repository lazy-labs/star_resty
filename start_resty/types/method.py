import abc
import inspect
from functools import wraps
from typing import Callable, ClassVar, Mapping, Type, Union

from marshmallow import Schema
from starlette.requests import Request
from starlette.responses import Response

from start_resty.operation import Operation
from start_resty.serializers import JsonSerializer, Serializer
from .parser import Parser

__all__ = ('Method', 'endpoint')


class ArgsParser:
    __slots__ = ('parsers', 'async_parsers')

    def __init__(self):
        self.parsers = []
        self.async_parsers = []


class MethodMeta(abc.ABCMeta):

    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs, **kwargs)

        func = getattr(cls, 'execute', None)
        if func is not None:
            cls.__parser__ = mcs.create_parser(func.__annotations__)

        cls._render_content = staticmethod(mcs.create_renders(cls))
        return cls

    @classmethod
    def create_renders(mcs, method):
        renders = []
        response_schema = getattr(method, 'response_schema', None)
        if response_schema is not None:
            if inspect.isclass(response_schema):
                response_schema = response_schema()

            renders.append(response_schema.dump)

        if method.serializer is not None:
            renders.append(mcs.render_bytes(method.serializer, method.status_code))

        def render(content):
            for r in renders:
                content = r(content)

            return content

        return render

    @staticmethod
    def create_parser(data: Mapping):
        args = ArgsParser()
        for key, value in data.items():
            parser = getattr(value, 'parser', None)
            if parser is None or not isinstance(parser, Parser):
                continue

            if inspect.iscoroutinefunction(parser.parse):
                args.async_parsers.append((key, parser))
            else:
                args.parsers.append((key, parser))

        return args

    @staticmethod
    def render_bytes(serializer, status_code):
        def render(content):
            return Response(serializer.render(content),
                            media_type=serializer.media_type,
                            status_code=status_code)

        return render


class Method(abc.ABC, metaclass=MethodMeta):
    __slots__ = ('request',)

    __parser__: ClassVar[ArgsParser]
    meta: ClassVar[Operation] = Operation(tag='default')
    serializer: ClassVar[Serializer] = JsonSerializer
    response_schema: ClassVar[Union[Schema, Type[Schema], None]] = None
    _render_content: ClassVar[Callable]
    status_code: int = 200

    def __init__(self, request: Request):
        self.request = request

    @abc.abstractmethod
    async def execute(self, *args, **kwargs):
        pass

    async def dispatch(self):
        kwargs = {}
        parser = self.__parser__
        for (key, p) in parser.parsers:
            kwargs[key] = p.parse(self.request)

        for (key, p) in parser.async_parsers:
            kwargs[key] = await p.parse(self.request)

        content = await self.execute(**kwargs)
        return self._render_content(content)

    @classmethod
    def as_endpoint(cls):
        return endpoint(cls)


def endpoint(cls: Type[Method]):
    @wraps(cls)
    async def wrapper(request: Request):
        method = cls(request)
        return await method.dispatch()

    wrapper.__endpoint__ = cls
    return wrapper
