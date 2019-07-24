from typing import Dict, List, Tuple

from starlette.requests import Request

from star_resty.types.parser import Parser


class RequestParser:
    __slots__ = ('parsers', 'async_parsers')

    def __init__(self):
        self.parsers: List[Tuple[str, Parser]] = []
        self.async_parsers: List[Tuple[str, Parser]] = []

    @property
    def is_empty(self) -> bool:
        return not (self.parsers or self.async_parsers)

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
