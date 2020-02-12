import ujson

__all__ = ('JsonSerializer',)


class JsonSerializer:
    media_type = 'application/json'

    @staticmethod
    def render(content) -> bytes:
        return ujson.dumps(content, ensure_ascii=False).encode('utf-8')
