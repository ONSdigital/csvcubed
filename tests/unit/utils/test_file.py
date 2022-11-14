from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from csvcubed.utils.file import copy_files_to_directory_with_structure


def test_copying_files_with_dir_structure():
    """
    Given the initial directory structure in tmp_dir_from:

        .
        └── level1
            ├── file1
            └── level2
                └── file2

    By specifying the paths of `file1` and `file2`, we should be able to copy those files *with* their directory
    structure into `tmp_dir_to`.
    """
    with TemporaryDirectory() as tmp_dir_from, TemporaryDirectory() as tmp_dir_to:
        level_1: Path = Path(tmp_dir_from) / "level1"
        level_1.mkdir()

        file_1 = level_1 / "file1"
        file_1.touch()

        level_2 = level_1 / "level2"
        level_2.mkdir()

        file_2 = level_2 / "file2"
        file_2.touch()

        copy_files_to_directory_with_structure(
            [file_1, file_2], tmp_dir_from, tmp_dir_to
        )

        expected_level_1 = Path(tmp_dir_to) / "level1"
        assert expected_level_1.exists()

        expected_file_1 = expected_level_1 / "file1"
        assert expected_file_1.exists()

        expected_level_2 = expected_level_1 / "level2"
        assert expected_level_2.exists()

        expected_file_2 = expected_level_2 / "file2"
        assert expected_file_2.exists()


if __name__ == "__main__":
    pytest.main()
