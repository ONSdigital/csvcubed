import unittest
from pathlib import Path
import pandas as pd


from csvqb.configloaders.infojson import get_cube_from_info_json
from csvqb.utils.qb.cube import validate_qb_component_constraints
from csvqb.models.cube import *
from csvqb.tests.unit.unittestbase import UnitTestBase


CWD = Path(".")
TEST_CASES_DIR = CWD / ".." / ".." / "test-cases" / "configloaders"
INFO_JSON_PATH = TEST_CASES_DIR / "info.json"
DATA_CSV_PATH = TEST_CASES_DIR / "data.csv"


class InfoJsonLoaderTests(UnitTestBase):
    def test_csv_cols_assumed_dimensions(self):
        """
            Assume that if a column isn't defined in the info.json `transform.columns` section, then it is a
            new locally defined dimension.

            Assert that the newly defined dimension has a codelist created from the values in the CSV.
        """
        data = pd.read_csv(DATA_CSV_PATH)
        cube = get_cube_from_info_json(INFO_JSON_PATH, data)

        matching_columns = [c for c in cube.columns if c.csv_column_title == "Undefined Column"]
        self.assertEqual(1, len(matching_columns))
        undefined_column_assumed_definition: CsvColumn = matching_columns[0]

        if not isinstance(undefined_column_assumed_definition, QbColumn):
            raise Exception("Incorrect type")

        self.assertIsInstance(undefined_column_assumed_definition.component, NewQbDimension)
        new_dimension: NewQbDimension = undefined_column_assumed_definition.component
        self.assertIsNotNone(new_dimension.code_list)

        if not isinstance(new_dimension.code_list, NewQbCodeList):
            raise Exception("Incorrect type")

        newly_defined_concepts = new_dimension.code_list.concepts

        self.assertTrue(1, len(newly_defined_concepts))

        new_concept = newly_defined_concepts.pop()
        self.assertEqual("Undefined Column Value", new_concept.label)

        errors = cube.validate()
        errors += validate_qb_component_constraints(cube)

        self.assert_no_validation_errors(errors)


if __name__ == '__main__':
    unittest.main()
