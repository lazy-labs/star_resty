from typing_extensions import Protocol


class Serializer(Protocol):
    media_type: str

    def render(self, resp) -> bytes:
        pass
