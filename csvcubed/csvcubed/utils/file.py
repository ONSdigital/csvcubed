"""
File
----

Utilities for files.
"""
import logging
import shutil
from pathlib import Path
from typing import Iterable


log = logging.getLogger(__name__)


def copy_files_to_directory_with_structure(
    files: Iterable[Path], common_parent: Path, to_dir: Path
) -> None:
    """
    Copies :obj:`files` into :obj:`to_dir` retaining the directory structure below :obj:`common_parent`.
    """
    for file in files:
        relative_dir_structure = file.relative_to(common_parent)
        abs_out_file_path = to_dir / relative_dir_structure

        _ensure_dir_structure_exists(abs_out_file_path.parent)
        log.debug("Copying %s to %s", file, abs_out_file_path)
        shutil.copy(file, abs_out_file_path)


def _ensure_dir_structure_exists(dir_path: Path) -> None:
    if not dir_path.exists():
        _ensure_dir_structure_exists(dir_path.parent)
        log.debug("Creating directory %s", dir_path)
        dir_path.mkdir()


def get_root_dir_level(end_file: str, start_dir: Path = Path(".")) -> Path:
    """
    Recursively moves backward in the dir tree until the end_file is found. If found, the current path is returned.
    """
    if str(start_dir) == "/":
        raise Exception("Could not find the root directory.")

    target_file = start_dir / end_file
    if target_file.exists():
        return start_dir

    return get_root_dir_level(end_file, start_dir.absolute().parent)
