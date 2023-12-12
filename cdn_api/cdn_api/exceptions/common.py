class CDNException(Exception):
    pass


class CDNClientException(CDNException):
    pass


class CDNServerException(CDNException):
    pass


class VideoUploadS3ServerException(CDNServerException):
    pass


class DBClientException(CDNClientException):
    pass


class DBServerException(CDNServerException):
    pass


class QueueServerException(CDNServerException):
    pass
