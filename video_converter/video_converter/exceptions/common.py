class VideoConverterError(Exception):
    pass


class VideoConverterOSError(VideoConverterError):
    pass


class VideoConverterDBError(VideoConverterError):
    pass


class VideoConverterMinioException(VideoConverterError):
    pass
