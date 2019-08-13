import abc
import inspect
from typing import Any, Callable, Tuple

from marshmallow import Schema
from marshmallow.exceptions import MarshmallowError
from starlette.responses import Response

from star_resty.exceptions import DumpError
from star_resty.types.parser import Parser
from .options import MethodMetaOptions
from .request_parser import RequestParser


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

            renders.append(mcs.dump_content(response_schema))

        if method.serializer is not None:
            renders.append(mcs.render_bytes(method.serializer, method.status_code or 200))

        return mcs.create_content_render(tuple(renders))

    @staticmethod
    def dump_content(response_schema: Schema):
        def dump(content):
            try:
                return response_schema.dump(content)
            except MarshmallowError as e:
                raise DumpError(e) from e
            except (ValueError, TypeError) as e:
                raise DumpError(e) from e

        return dump

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
