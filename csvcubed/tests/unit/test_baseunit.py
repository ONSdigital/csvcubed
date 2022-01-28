from pathlib import Path
from typing import List

from csvcubed.models.validationerror import ValidationError


def get_test_base_dir() -> Path:
    path_parts = Path(".").absolute().parts
    if "tests" in path_parts:
        test_index = path_parts.index("tests")
        test_root_path = Path(*path_parts[0 : test_index + 1])
    else:  # Fine Rob, you win.
        # Use deepest instance of "csvcubed" so I can call my cloned repository folder "csvcubed" too.
        csvwlib_index = len(path_parts) - (
            1 + list(reversed(path_parts)).index("csvcubed")
        )
        # Removed double csvcubed because tox is run in the first csvcubed directory not csvcubed/tests.
        csvcubed_path = Path(*path_parts[0 : csvwlib_index + 1])
        tests_folders = list(csvcubed_path.rglob("tests"))
        if len(tests_folders) == 0:
            raise Exception(f"Could not find 'tests' folder in {csvcubed_path}")        
        elif len(tests_folders) > 1:
            # Can't raise an exception here else VSCode gets unhappy running the unit tests.
            print(f"Found multiple 'tests' folders in {csvcubed_path}")        

    return (tests_folders[0])


def get_test_cases_dir() -> Path:
    return get_test_base_dir() / "test-cases"


def assert_num_validation_errors(
    errors: List[ValidationError], num_errors_expected: int
):
    assert len(errors) == num_errors_expected, ", ".join([e.message for e in errors])
