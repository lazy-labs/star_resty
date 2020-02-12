from dataclasses import dataclass
from typing import Optional, Sequence, Any, Mapping

__all__ = ('Operation',)


@dataclass(frozen=True)
class Operation:
    tag: str = 'default'
    description: Optional[str] = None
    summary: Optional[str] = None
    errors: Sequence[Any] = ()
    security: Optional[Sequence] = None
    meta: Optional[Mapping] = None

    @classmethod
    def create(cls,
               tag: str = 'default',
               description: Optional[str] = None,
               summary: Optional[str] = None,
               errors: Sequence[Any] = (),
               security: Optional[Sequence] = None,
               **kwargs) -> 'Operation':
        return cls(tag=tag, description=description,
                   summary=summary, errors=errors,
                   security=security, meta=kwargs)
