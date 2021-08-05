from pathlib import Path
from typing import List

from csvqb.models.validationerror import ValidationError


def get_test_base_dir() -> Path:
    path_parts = Path(".").absolute().parts
    test_index = path_parts.index("tests")
    test_root_path = Path(*path_parts[0: test_index + 1])
    return test_root_path


def get_test_cases_dir() -> Path:
    return get_test_base_dir() / "test-cases"


def assert_num_validation_errors(
    errors: List[ValidationError], num_errors_expected: int
):
    assert num_errors_expected == len(errors), ", ".join([e.message for e in errors])
