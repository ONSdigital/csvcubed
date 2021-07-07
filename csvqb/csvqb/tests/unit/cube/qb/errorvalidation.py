import unittest
import pandas as pd


from csvqb.models.cube import *
from csvqb.models.rdf import URI
from csvqb.utils.qb.cube import validate_qb_component_constraints
from csvqb.tests.unit.unittestbase import UnitTestBase


class InternalApiLoaderTests(UnitTestBase):
    def test_single_measure_qb_definition(self):
        """
            Single-measure Qbs can be defined.
        """
        data = pd.DataFrame({
            "Existing Dimension": ["A", "B", "C"],
            "Local Dimension": ["D", "E", "F"],
            "Value": [2, 2, 2]
        })

        metadata = CubeMetadata(URI("http://example.com/some/dataset"), "Some Dataset")
        columns = [
            QbColumn("Existing Dimension", ExistingQbDimension("https://example.org/dimensions/existing_dimension")),
            QbColumn("Local Dimension", NewQbDimension.from_data("Dimension of letters", data["Local Dimension"])),
            QbColumn("Value",
                     QbSingleMeasureObservationValue(
                         ExistingQbMeasure("http://example.com/measures/existing_measure"),
                         NewQbUnit("some new unit")
                     ))
        ]

        cube = Cube(metadata, data, columns)
        validation_errors = cube.validate()
        validation_errors += validate_qb_component_constraints(cube)

        self.assert_no_validation_errors(validation_errors)

    def test_multi_measure_qb_definition(self):
        """
            Multi-measure Qbs can be defined.
        """
        data = pd.DataFrame({
            "Existing Dimension": ["A", "B", "C"],
            "Value": [2, 2, 2],
            "Measure": ["People", "Children", "Adults"],
            "Units": ["Percent", "People", "People"]
        })

        metadata = CubeMetadata(URI("http://example.com/some/dataset"), "Some Dataset")
        columns = [
            QbColumn("Existing Dimension", ExistingQbDimension("https://example.org/dimensions/existing_dimension")),
            QbColumn("Value", QbMultiMeasureObservationValue("number")),
            QbColumn("Measure", QbMultiMeasureDimension.new_measures_from_data(data["Measure"])),
            QbColumn("Units", QbMultiUnits.new_units_from_data(data["Units"]))
        ]

        cube = Cube(metadata, data, columns)
        validation_errors = cube.validate()
        validation_errors += validate_qb_component_constraints(cube)

        self.assert_no_validation_errors(validation_errors)


if __name__ == '__main__':
    unittest.main()
