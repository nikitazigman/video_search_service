from stream_api.core.exceptions import ServiceError


class IntegrationError(ServiceError):
    ...


class IntegrationAPIClientError(IntegrationError):
    ...
