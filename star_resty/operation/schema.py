from typing import Any, NamedTuple, Optional, Sequence


class Operation(NamedTuple):
    tag: str = 'default'
    description: Optional[str] = None
    summary: Optional[str] = None
    errors: Sequence[Any] = ()
    security: Optional[Sequence] = None

    def update(self, **kwargs):
        return self._replace(**kwargs)
