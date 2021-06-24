import unittest
from abc import ABC
from typing import List
import json


from csvqb.models.validationerror import ValidationError


class UnitTestBase(unittest.TestCase, ABC):
    def assert_no_validation_errors(self, errors: List[ValidationError]) -> None:
        if len(errors) > 0:
            raise Exception(json.dumps([error.__dict__ for error in errors], indent=4))

