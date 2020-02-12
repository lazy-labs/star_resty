from typing_extensions import Protocol

__all__ = ('Serializer',)


class Serializer(Protocol):
    media_type: str

    def render(self, resp) -> bytes:
        pass
