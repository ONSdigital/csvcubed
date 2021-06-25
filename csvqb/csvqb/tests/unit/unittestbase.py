import unittest
from abc import ABC
from typing import List
import json
from pathlib import Path


from csvqb.models.validationerror import ValidationError


class UnitTestBase(unittest.TestCase, ABC):
    def get_test_base_dir(self) -> Path:
        path_parts = Path(".").absolute().parts
        test_index = path_parts.index("tests")
        test_root_path = Path(*path_parts[0:test_index+1])
        return test_root_path

    def get_test_cases_dir(self) -> Path:
        return self.get_test_base_dir() / "test-cases"

    def assert_no_validation_errors(self, errors: List[ValidationError]) -> None:
        if len(errors) > 0:
            raise Exception(json.dumps([error.__dict__ for error in errors], indent=4))

