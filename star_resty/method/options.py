from typing import Callable

from .request_parser import RequestParser


class MethodMetaOptions:
    __slots__ = ('parser', 'render')

    def __init__(self, request_parser: RequestParser, render: Callable):
        self.parser = request_parser
        self.render = render
