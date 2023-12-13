import dataclasses
import pathlib
import typing as tp
import uuid

import fastapi
import structlog

from stream_api import repositories as repos
from stream_api.services.exceptions import (
    S3ObjectNotFoundHTTPError,
    VideoNotFoundHTTPError,
)
from stream_api.utils.files import read_file, write_file


logger = structlog.get_logger()


@dataclasses.dataclass
class S3VideoObjectPath:
    main_dir_name: str
    hlc_dir_name: str
    object_name_stemmed: str
    extension: str

    @classmethod
    def from_name_and_resolution(
        cls, video_name: str, video_resolution: int
    ) -> "S3VideoObjectPath":
        video_name_stemmed, ext = video_name.split(".")
        return S3VideoObjectPath(
            main_dir_name=video_name_stemmed,
            hlc_dir_name=f"hlc-{video_resolution}",
            object_name_stemmed=video_name_stemmed,
            extension=ext,
        )

    @property
    def full_path(self) -> str:
        return (
            f"{self.main_dir_name}/{self.hlc_dir_name}/"
            f"{self.object_name_stemmed}.{self.extension}"
        )

    @property
    def dir_path(self) -> str:
        return f"{self.main_dir_name}/{self.hlc_dir_name}"

    @property
    def name(self) -> str:
        return f"{self.object_name_stemmed}.{self.extension}"


class VideoManifestFileServiceProtocol(tp.Protocol):
    async def generate_video_manifest_file(
        self, video_id: uuid.UUID, video_resolution: int, s3_urls_expire_in_secs: int
    ) -> pathlib.Path:
        ...


class VideoManifestFileService:
    def __init__(
        self,
        video_meta_repo: repos.VideoMetaRepositoryProtocol,
        s3_repo: repos.S3RepositoryProtocol,
        tmp_dir: pathlib.Path,
    ) -> None:
        self.video_meta_repo = video_meta_repo
        self.s3_repo = s3_repo
        self.tmp_dir = tmp_dir

        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    async def generate_video_manifest_file(
        self,
        video_id: uuid.UUID,
        video_resolution: int,
        s3_urls_expire_in_secs: int,
    ) -> pathlib.Path:
        await logger.debug(
            "Get video meta info from DB",
            video_id=video_id,
            video_resolution=video_resolution,
        )

        if video_meta := await self.video_meta_repo.get_by_id(video_id=video_id):
            s3_video_obj_path = S3VideoObjectPath.from_name_and_resolution(
                video_name=video_meta.name, video_resolution=video_resolution
            )
            filename_s3url_map = await self._get_s3_urls(
                bucket_name=video_meta.bucket_hlc,
                dir_name=s3_video_obj_path.dir_path,
                expire_in_secs=s3_urls_expire_in_secs,
            )

            s3_manifest_obj_path = S3VideoObjectPath(
                main_dir_name=s3_video_obj_path.main_dir_name,
                hlc_dir_name=s3_video_obj_path.hlc_dir_name,
                object_name_stemmed=s3_video_obj_path.object_name_stemmed,
                extension="m3u8",
            )
            tmp_manifest_filepath = (
                pathlib.Path(self.tmp_dir) / s3_manifest_obj_path.name
            )

            original_manifest_filepath = await self.s3_repo.download_file(
                bucket_name=video_meta.bucket_hlc,
                object_name=s3_manifest_obj_path.full_path,
                target_filepath=tmp_manifest_filepath,
            )
            return await self._create_video_manifest_file(
                src_filepath=original_manifest_filepath,
                target_filepath=tmp_manifest_filepath,
                replace_map=filename_s3url_map,
            )

        await logger.error("Video is not found", id=video_id)

        raise VideoNotFoundHTTPError

    async def _get_s3_urls(
        self, bucket_name: str, dir_name: str, expire_in_secs: int
    ) -> dict[str, str]:
        """Get presigned s3 URLs for each object at the given bucket dir.

        Arg:
            bucket_name: Name of an S3 bucket.
            dir_name: S3 path within the S3 bucket.

        Returns:
            dict[str, str]: Dictionary (key is s3 object relative filename,
            value is a presigned s3 url).
        """

        await logger.debug(
            "Get presigned s3 urls for objects in the bucket dir",
            bucket_name=bucket_name,
            dir_name=dir_name,
        )

        s3_objs = await self.s3_repo.list_objects(
            bucket_name=bucket_name, dir_name=dir_name
        )
        if not s3_objs:
            await logger.error(
                "S3 objects are not found in the bucket dir",
                bucket_name=bucket_name,
                dir_name=dir_name,
            )

            raise S3ObjectNotFoundHTTPError

        filename_url_map = {}
        for obj in s3_objs:
            url = await self.s3_repo.get_presigned_url(
                bucket_name=bucket_name,
                s3_object=obj,
                expires_in_secs=expire_in_secs,
                method="GET",
            )
            filename = obj.object_name.split("/")[-1]
            filename_url_map[filename] = url

        return filename_url_map

    @staticmethod
    async def _create_video_manifest_file(
        src_filepath: pathlib.Path,
        target_filepath: pathlib.Path,
        replace_map: dict,
    ) -> pathlib.Path:
        await logger.debug("Create new video manifest file")

        content = await read_file(filepath=src_filepath)
        for k, v in replace_map.items():
            content = content.replace(k, v)

        return await write_file(filepath=target_filepath, content=content)


async def get_video_manifest_service(
    video_meta_repo: tp.Annotated[
        repos.VideoMetaRepositoryProtocol, fastapi.Depends(repos.get_video_meta_repo)
    ],
    s3_repo: tp.Annotated[
        repos.S3RepositoryProtocol, fastapi.Depends(repos.get_s3_repository)
    ],
) -> VideoManifestFileServiceProtocol:
    return VideoManifestFileService(
        video_meta_repo=video_meta_repo,
        s3_repo=s3_repo,
        tmp_dir=pathlib.Path.cwd() / pathlib.Path("./tmp"),
    )
