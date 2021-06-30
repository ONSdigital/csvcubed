import unittest
from pathlib import Path
import pandas as pd

import csvqb.writers.qb
from csvqb.configloaders.infojson import get_cube_from_info_json
from csvqb.utils.qb.cube import validate_qb_component_constraints
from csvqb.models.cube import *
from csvqb.tests.unit.unittestbase import UnitTestBase


class InfoJsonLoaderTests(UnitTestBase):
    def test_csv_cols_assumed_dimensions(self):
        """
            If a column isn't defined, assume it is a new local dimension.

            Assume that if a column isn't defined in the info.json `transform.columns` section, then it is a
            new locally defined dimension.

            Assert that the newly defined dimension has a codelist created from the values in the CSV.
        """
        data = pd.read_csv(self.get_test_cases_dir() / "configloaders" / "data.csv")
        cube = get_cube_from_info_json(self.get_test_cases_dir() / "configloaders" / "info.json", data)

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

        newly_defined_concepts = list(new_dimension.code_list.concepts)

        self.assertTrue(1, len(newly_defined_concepts))

        new_concept = newly_defined_concepts[0]
        self.assertEqual("Undefined Column Value", new_concept.label)

        errors = cube.validate()
        errors += validate_qb_component_constraints(cube)

        self.assert_no_validation_errors(errors)

        csvqb.writers.qb.write_metadata(cube, self.get_test_cases_dir() / "output.csv-metadata.json")


if __name__ == '__main__':
    unittest.main()
