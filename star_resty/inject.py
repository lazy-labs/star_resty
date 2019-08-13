import operator
from typing import TypeVar, Type, Optional, Generic

from star_resty import Method

__all__ = ('attr',)

T = TypeVar('T')


class InjectAttr(Generic[T]):
    __slots__ = ('_func',)

    def __init__(self, name=None):
        if name:
            self._func = operator.attrgetter(name)
        else:
            self._func = None

    def __set_name__(self, owner, name):
        if self._func is None:
            self._func = operator.attrgetter(name)

    def __get__(self, instance: Optional[Method], owner: Type[Method]) -> T:
        if instance is None:
            return self

        return self._func(instance.request.app)


def attr(_: Optional[Type[T]] = None, *, name: Optional[str] = None) -> T:
    return InjectAttr[T](name)
