"""
File
----

Utilities for files.
"""
import json
import logging
import shutil
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Iterable


_logger = logging.getLogger(__name__)


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
        _logger.debug("Copying %s to %s", file, abs_out_file_path)
        shutil.copy(file, abs_out_file_path)


def _ensure_dir_structure_exists(dir_path: Path) -> None:
    if not dir_path.exists():
        _ensure_dir_structure_exists(dir_path.parent)
        _logger.debug("Creating directory %s", dir_path)
        dir_path.mkdir()


def read_json_from_file(file_path: Path, log: logging.RootLogger) -> dict:
    """
    Reads the json content of the file located at file_path
    Returns the decoded json as a dict
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)

    except FileNotFoundError as err:
        log.error(f"File Not Found Error when looking for: {file_path}")

    except JSONDecodeError as err:
        log.error(f"JSON Decode Error: {repr(err)}")
        raise err

    except TypeError as err:
        log.error(f"JSON Type Error: {repr(err)}")
        raise err

    except Exception as err:
        log.error(f"{type(err)} exception raised because: {repr(err)}")
        raise err
