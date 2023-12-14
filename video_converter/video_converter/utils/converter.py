import subprocess
from pathlib import Path
from typing import Protocol

from video_converter.exceptions import VideoConverterOSError

from asgiref.sync import sync_to_async


class VideoConverterProtocol(Protocol):
    async def convert(
        self,
        file_path: Path,
        frame_size: str,
        output_path: Path,
    ) -> None:
        """
        Convert video to hlc format.
        """


class VideoConverter:
    hls_time = 10
    start_number = 0
    level = 3.0
    profile = "baseline"
    hls_list_size = 0

    def get_cmd(
        self,
        file_path: Path,
        frame_size: str,
        output_path: str,
    ) -> str:
        return (
            f"ffmpeg -i {file_path} -profile:v {self.profile} "
            f"-level {self.level} -s {frame_size} "
            f"-start_number {self.start_number} -hls_time "
            f"{self.hls_time} -hls_list_size {self.hls_list_size} "
            f"-f hls {output_path}"
        )

    @sync_to_async
    def convert(
        self,
        file_path: Path,
        frame_size: str,
        output_path: Path,
    ) -> None:
        cmd = self.get_cmd(
            file_path=file_path,
            frame_size=frame_size,
            output_path=str(output_path),
        )

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as process:
                process.communicate()
                if process.returncode != 0:
                    raise RuntimeError("Error while converting video.")
        except (OSError, RuntimeError, subprocess.SubprocessError) as e:
            raise VideoConverterOSError from e


def get_video_converter() -> VideoConverter:
    return VideoConverter()
