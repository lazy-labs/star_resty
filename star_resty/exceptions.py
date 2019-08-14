from typing import Dict, Optional

from marshmallow.exceptions import ValidationError

__all__ = ('StarRestError', 'DumpError', 'DecodeError')


class StarRestError(Exception):
    pass


class DumpError(StarRestError):

    def __init__(self, exc: Optional[Exception] = None, *args):
        super().__init__(*args)
        self.orig_exc = exc

    def normalized_messages(self) -> Dict:
        if self.orig_exc is not None and isinstance(self.orig_exc, ValidationError):
            return self.orig_exc.normalized_messages()

        return {'_schema': 'Error dump content'}


class DecodeError(StarRestError):

    def normalized_messages(self) -> Dict:
        return {'_body': str(self)}
