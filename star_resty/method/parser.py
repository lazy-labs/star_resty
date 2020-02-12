import inspect
import itertools
from dataclasses import is_dataclass, fields
from functools import partial
from typing import Dict, Tuple, Sequence, Generator, Mapping, Generic, TypeVar, Type, Callable, Optional, Any, Union

from starlette.requests import Request

from star_resty.payload.parser import Parser

__all__ = ('RequestParser', 'create_parser')

D = TypeVar('D')


class RequestParser:
    __slots__ = ('_parsers', '_async_parsers')

    def __init__(self, parsers: Sequence[Tuple[str, Union[Parser, 'RequestParser']]] = (),
                 async_parsers: Sequence[Tuple[str, Union[Parser, 'RequestParser']]] = ()):
        self._parsers = parsers
        self._async_parsers = async_parsers

    def __nonzero__(self):
        return bool(self._parsers or self._async_parsers)

    def __iter__(self) -> Generator[Parser, None, None]:
        parsers = itertools.chain(self._parsers, self._async_parsers)
        for (_, p) in parsers:
            if isinstance(p, RequestParser):
                yield from p
            else:
                yield p

    async def parse(self, request: Request) -> Dict:
        params = {}
        for (key, p) in self._parsers:
            params[key] = p.parse(request)

        for (key, p) in self._async_parsers:
            params[key] = await p.parse(request)

        return params


class DataClassParser(RequestParser, Generic[D]):
    __slots__ = ('_data_cls',)

    def __init__(self, data_cls: Type[D], parsers: Sequence[Tuple[str, Parser]] = (),
                 async_parsers: Sequence[Tuple[str, Parser]] = ()):
        super().__init__(parsers=parsers, async_parsers=async_parsers)
        self._data_cls = data_cls

    async def parse(self, request: Request) -> D:
        params = await super().parse(request)
        return self._data_cls(**params)


def create_parser(func) -> RequestParser:
    if func is None:
        return RequestParser()

    return create_parser_from_data(func.__annotations__)


def create_parser_from_data(data: Mapping) -> RequestParser:
    parsers = []
    async_parsers = []
    for key, value in data.items():
        if is_dataclass(value):
            data = {field.name: field.type for field in fields(value)}
            factory = partial(DataClassParser, value)
            parser = create_parser_for_dc(data, factory=factory)
        else:
            parser = getattr(value, 'parser', None)

        if parser is None or not isinstance(parser, (Parser, RequestParser)):
            continue

        if inspect.iscoroutinefunction(parser.parse):
            async_parsers.append((key, parser))
        else:
            parsers.append((key, parser))

    return RequestParser(parsers=parsers, async_parsers=async_parsers)


def create_parser_for_dc(data: Mapping, factory: Callable) -> RequestParser:
    parsers = []
    async_parsers = []
    for key, value in data.items():
        if is_dataclass(value):
            data = {field.name: field.type for field in fields(value)}
            factory = partial(DataClassParser, value)
            parser = create_parser_for_dc(data, factory=factory)
        else:
            parser = getattr(value, 'parser', None)

        if parser is None:
            parser = get_parser_from_args(value)

        if parser is None or not isinstance(parser, (Parser, RequestParser)):
            continue

        if inspect.iscoroutinefunction(parser.parse):
            async_parsers.append((key, parser))
        else:
            parsers.append((key, parser))

    return factory(parsers=parsers, async_parsers=async_parsers)


def get_parser_from_args(value: Any) -> Optional[Parser]:
    args = getattr(value, '__args__', None) or ()
    for a in args:
        parser = getattr(a, 'parser', None)
        if parser is not None and isinstance(parser, Parser):
            return parser
