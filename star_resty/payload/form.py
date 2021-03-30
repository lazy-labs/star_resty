import types
from typing import Mapping, Type, TypeVar, Union

from marshmallow import EXCLUDE, Schema
from starlette.requests import Request

from star_resty.exceptions import DecodeError
from .parser import Parser, set_parser

__all__ = ('form_schema', 'form_payload', 'FormParser')

P = TypeVar('P')


def form_schema(schema: Union[Schema, Type[Schema]], cls: P,
                unknown: str = EXCLUDE) -> P:
    return types.new_class('FormDataInputParams', (cls,),
                           exec_body=set_parser(FormParser.create(schema, unknown=unknown)))


def form_payload(schema: Union[Schema, Type[Schema]], unknown=EXCLUDE) -> Type[Mapping]:
    return form_schema(schema, Mapping, unknown=unknown)


class FormParser(Parser):
    __slots__ = ()

    @property
    def location(self):
        return 'body'

    @property
    def media_type(self):
        return 'multipart/form-data'

    async def parse(self, request: Request):
        try:
            form_data = await request.form()
            form_data = {} if not form_data else form_data
        except Exception as e:
                raise DecodeError('Invalid form data: %s' % (str(e))) from e
        return self.schema.load(form_data, unknown=self.unknown)
