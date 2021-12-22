from pathlib import Path
from typing import List

from csvcubed.models.validationerror import ValidationError


def get_test_base_dir() -> Path:
    path_parts = Path(".").absolute().parts
    if "tests" in path_parts:
        test_index = path_parts.index("tests")
        test_root_path = Path(*path_parts[0 : test_index + 1])
    else:  # Fine Rob, you win.
        csvwlib_index = path_parts.index("csvcubed")
        # Removed double csvcubed because tox is run in the first csvcubed directory not csvcubed/tests.
        test_root_path = Path(*path_parts[0 : csvwlib_index + 1], "tests")
    return test_root_path


def get_test_cases_dir() -> Path:
    return get_test_base_dir() / "test-cases"


def assert_num_validation_errors(
    errors: List[ValidationError], num_errors_expected: int
):
    assert len(errors) == num_errors_expected, ", ".join([e.message for e in errors])
