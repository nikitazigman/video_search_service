import pathlib

import aiofiles


async def read_file(filepath: pathlib.Path) -> str:
    async with aiofiles.open(filepath, "r") as f:
        return await f.read()


async def write_file(filepath: pathlib.Path, content: str) -> pathlib.Path:
    async with aiofiles.open(filepath, mode="w") as f:
        await f.write(content)
    return filepath


def remove_file(filepath: pathlib.Path) -> None:
    pathlib.Path(filepath).unlink(missing_ok=True)
