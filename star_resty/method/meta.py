import abc

from .parser import create_parser
from .render import create_render

__all__ = ('MethodMeta',)


class MethodMeta(abc.ABCMeta):

    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs, **kwargs)

        func = getattr(cls, 'execute', None)
        if func is None:
            raise TypeError(f'Invalid method class={name}')

        cls.__parser__ = create_parser(func)
        cls.__render__ = create_render(cls)
        return cls
