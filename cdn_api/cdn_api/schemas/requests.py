from fastapi import Form, UploadFile


class UploadZipArchive:
    def __init__(
        self,
        zip_archive: UploadFile,
        path: str = Form(),
    ):
        self.zip_archive = zip_archive
        self.path = path
