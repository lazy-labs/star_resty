from typing import Any

from starlette.applications import Starlette
from starlette.responses import JSONResponse

__all__ = (
    'ServiceApiError', 'BadRequestError', 'AuthError', 'ForbiddenError', 'NotFoundError', 'ServerError', 'GatewayError',
    'ConflictError', 'register_error_handler')


class BaseApiException(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)

        if status_code is not None:
            self.status_code = status_code


class ServiceApiError(BaseApiException):
    status_code = 500

    def __init__(self, message, status_code=None, errors=None):
        super().__init__(message, status_code=status_code or self.status_code)
        self.message = message
        self.errors = errors


class BadRequestError(ServiceApiError):
    status_code = 400

    def __init__(self, message='Bad request', errors=None):
        super().__init__(message, errors=errors)


class AuthError(ServiceApiError):
    status_code = 401

    def __init__(self, message: str = 'Unauthorized', errors=None):
        super().__init__(message=message, errors=errors)


class ForbiddenError(ServiceApiError):
    status_code = 403

    def __init__(self, message: str = 'Forbidden', errors=None):
        super().__init__(message=message, errors=errors)


class NotFoundError(ServiceApiError):
    status_code = 404

    @classmethod
    def create(cls, entity_id: Any):
        return cls(errors={'id': [f'Object with `{entity_id}` is not found']})

    def __init__(self, message='Not found', errors=None):
        super().__init__(message, errors=errors)


class ServerError(ServiceApiError):
    status_code = 500

    def __init__(self, message='Internal Server Error', errors=None):
        super().__init__(message, errors=errors)


class GatewayError(ServiceApiError):
    status_code = 503

    def __init__(self, message='Gateway Error', errors=None):
        super().__init__(message, errors=errors)


class ConflictError(ServiceApiError):
    status_code = 409

    @classmethod
    def create(cls, entity_id: Any):
        return cls(errors={'id': [f'Object with `{entity_id}` already exists']})

    def __init__(self, message='Conflict', errors=None):
        super().__init__(message, errors=errors)


def register_error_handler(app: Starlette):
    @app.exception_handler(ServiceApiError)
    async def error(request, exc: ServiceApiError):
        return JSONResponse({'success': False, 'result': {'message': exc.message}}, status_code=exc.status_code)
