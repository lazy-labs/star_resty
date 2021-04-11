import abc
from typing import Optional, Any, Sequence, Mapping, Type

from marshmallow import ValidationError
from starlette.datastructures import UploadFile
from starlette.requests import Request

from .base import Parser

__all__ = ('upload',)


class UploadSequence(Sequence[UploadFile], metaclass=abc.ABCMeta):
    pass


def upload(*args: str,
           description: Optional[str] = None,
           required: bool = False) -> Type[UploadSequence]:
    def helper() -> Any:
        return UploadParser(args, description=description, required=required)

    return helper()


class UploadParser(Parser):

    def __init__(self, file_names: Sequence[str] = (), *,
                 description: Optional[str] = None,
                 required: bool = False):
        self.files_names = frozenset(file_names)
        self.description = description
        self.required = required

    @property
    def parser(self):
        return self

    @property
    def media_type(self):
        return 'multipart/form-data'

    @property
    def location(self):
        return 'formData'

    async def parse(self, request: Request):
        form = await request.form()
        res = []
        for key, val in form.items():
            if not isinstance(val, UploadFile):
                continue

            if not self.files_names or key in self.files_names:
                res.append(val)

        if self.required and not res:
            raise ValidationError(message='Missing required file', field_name='form')

        return res

    def get_spec(self):
        if self.files_names:
            for name in sorted(self.files_names):
                yield self._create_spec(name)
        else:
            yield self._create_spec('upfile')

    def _create_spec(self, name: str) -> Mapping:
        return {
            'in': 'formData',
            'type': 'file',
            'description': self.description or '',
            'name': name,
            'required': self.required
        }
