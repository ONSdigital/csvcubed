import pytest
from abc import ABC
from typing import List
import json
from pathlib import Path


def get_test_base_dir() -> Path:
    path_parts = Path(".").absolute().parts
    test_index = path_parts.index("tests")
    test_root_path = Path(*path_parts[0:test_index+1])
    return test_root_path

    # return Path(".").absolute() / "csvqb" / "tests"


def get_test_cases_dir() -> Path:
    return get_test_base_dir() / "test-cases"
