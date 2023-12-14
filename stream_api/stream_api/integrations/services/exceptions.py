from starlette import status

from stream_api.core.exceptions import ServiceError, ServiceHTTPError


class AuthServiceError(ServiceError):
    ...


class AuthenticationError(ServiceHTTPError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid authentication credentials were provided."
