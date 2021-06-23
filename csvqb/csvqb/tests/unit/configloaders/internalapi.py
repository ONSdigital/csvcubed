import unittest
import pandas as pd


from csvqb.models.cube import *
from csvqb.models.rdf import URI
from csvqb.utils.qb.cube import validate_qb_component_constraints


class InternalApiLoaderTests(unittest.TestCase):
    def test_something(self):
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
                         NewQbUnit("Some new unit.")))
        ]

        cube = Cube(metadata, data, columns)
        validation_errors = cube.validate()
        validation_errors += validate_qb_component_constraints(cube)

        self.assertTrue(cube is not None)


if __name__ == '__main__':
    unittest.main()
