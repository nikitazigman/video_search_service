from pathlib import Path
from zipfile import ZipInfo

from cdn_api.schemas.file_info_repo import InsertFileSchema


def transform_zip_info_to_insert_file(
    files_info: list[ZipInfo], path: Path
) -> list[InsertFileSchema]:
    return [
        InsertFileSchema(
            name=zip_info.filename,
            path=path / zip_info.filename,
        )
        for zip_info in files_info
    ]
