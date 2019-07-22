from typing import NamedTuple, Optional, Type, Union

from marshmallow import Schema


class Operation(NamedTuple):
    tag: str = 'default'
    description: Optional[str] = None
    summary: Optional[str] = None
    status: int = 200
