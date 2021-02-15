import abc
from functools import wraps
from typing import ClassVar, Type, Union, Optional, Callable, Any

from marshmallow import Schema
from starlette.requests import Request
from starlette.responses import Response

from star_resty.operation import Operation
from star_resty.serializers import JsonSerializer, Serializer
from .meta import MethodMeta

__all__ = ('Method', 'endpoint')


class Method(abc.ABC, metaclass=MethodMeta):
    __slots__ = ('request',)
    __parser__: ClassVar[Callable[[Request], Any]]
    __render__: ClassVar[Callable[[Any], Response]]

    meta: ClassVar[Operation] = Operation(tag='default')
    serializer: ClassVar[Serializer] = JsonSerializer
    response_schema: ClassVar[Union[Schema, Type[Schema], None]] = None
    Response: ClassVar[Optional[Type[Schema]]] = None
    status_code: int = 200

    def __init__(self, request: Request):
        self.request = request

    @abc.abstractmethod
    async def execute(self, *args, **kwargs):
        pass

    async def dispatch(self) -> Response:
        params = await self.__parser__.parse(self.request)
        content = await self.execute(**params)
        return self.__render__(content, self)

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
