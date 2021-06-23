import unittest
import pandas as pd


from csvqb.models.cube import *
from csvqb.models.rdf import URI


class InternalApiLoaderTests(unittest.TestCase):

    def test_column_not_configured_error(self):
        """
            If the CSV data contains a column which is not defined, we get an error.
        """

        data = pd.DataFrame({
            "Some Dimension": ["A", "B", "C"]
        })

        metadata = CubeMetadata(URI("http://example.com/some/dataset"), "Some Dataset")
        columns = []
        cube = Cube(metadata, data, columns)
        validation_errors = cube.validate()

        self.assertEqual(1, len(validation_errors))
        error = validation_errors[0]
        self.assertTrue("Some Dimension" in error.message)

    def test_column_title_wrong_error(self):
        """
            If the Cube object contains a column title which is not defined in the CSV data, we get an error.
        """

        data = pd.DataFrame()

        metadata = CubeMetadata(URI("http://example.com/some/dataset"), "Some Dataset")
        columns = [
            SuppressedCsvColumn("Some Column Title")
        ]
        cube = Cube(metadata, data, columns)
        validation_errors = cube.validate()

        self.assertEqual(1, len(validation_errors))
        error = validation_errors[0]
        self.assertTrue("Some Column Title" in error.message)


if __name__ == '__main__':
    unittest.main()
