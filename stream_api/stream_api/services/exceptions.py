from starlette import status

from stream_api.core.exceptions import ServiceHTTPError


class VideoNotFoundHTTPError(ServiceHTTPError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Video not found"


class S3ObjectNotFoundHTTPError(ServiceHTTPError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "S3 object not found"
