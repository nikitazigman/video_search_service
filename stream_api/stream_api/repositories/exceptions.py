from stream_api.core.exceptions import ServiceError


class RepositoryError(ServiceError):
    ...


class S3RepositoryError(RepositoryError):
    ...


class S3BucketDoesNotExistError(S3RepositoryError):
    ...


class PostgresRepositoryError(RepositoryError):
    ...
