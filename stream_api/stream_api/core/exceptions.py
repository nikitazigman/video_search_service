import fastapi.exceptions

from starlette import status


class BaseServiceError(Exception):
    ...


class ServiceHTTPError(fastapi.exceptions.HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = ""

    def __init__(
        self, status_code: int | None = None, detail: str | None = None
    ) -> None:
        super().__init__(
            status_code=status_code or self.status_code, detail=detail or self.detail
        )
