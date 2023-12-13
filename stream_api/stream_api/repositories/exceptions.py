from stream_api.core.exceptions import BaseServiceError


class S3RepositoryError(BaseServiceError):
    ...


class S3BucketDoesNotExistError(S3RepositoryError):
    ...
