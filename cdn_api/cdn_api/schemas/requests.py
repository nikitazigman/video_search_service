from uuid import UUID

from fastapi import UploadFile


class VideoUploadRequest:
    def __init__(self, file: UploadFile, video_id: UUID) -> None:
        self.file = file
        self.video_id = video_id
