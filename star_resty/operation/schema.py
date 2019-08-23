from typing import Any, NamedTuple, Optional, Sequence


class Operation(NamedTuple):
    tag: str = 'default'
    description: Optional[str] = None
    summary: Optional[str] = None
    errors: Sequence[Any] = ()
