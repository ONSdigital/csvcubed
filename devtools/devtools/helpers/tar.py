"""
Tar Archives
------------
"""
from io import BytesIO
from pathlib import Path
from tarfile import TarFile
import os
from typing import Iterable


def dir_to_tar(directory: Path) -> BytesIO:
    if not directory.is_dir():
        raise Exception("Input must be a directory.")

    archive = BytesIO()
    with TarFile(fileobj=archive, mode="w") as tar_file:
        tar_file: TarFile
        for root, dirs, files in os.walk(directory):
            for file in files:
                path_from_root = Path(os.path.join(root, file))
                path_from_directory = path_from_root.relative_to(directory)
                tar_file.add(path_from_root, arcname=str(path_from_directory))
    archive.seek(0)

    return archive


def extract_tar(output_stream: Iterable[bytes], output_directory: Path) -> None:
    output_archive = BytesIO()
    for line in output_stream:
        output_archive.write(line)
    output_archive.seek(0)
    with TarFile(fileobj=output_archive, mode="r") as t:
        t.extractall(path=output_directory)
