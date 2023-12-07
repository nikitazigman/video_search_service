from fastapi import Form, UploadFile


class UploadVideo:
    def __init__(
        self,
        video: UploadFile,
        name: str = Form(),
        bucket: str = Form(),
    ):
        self.video = video
        self.name = name
        self.bucket = bucket
