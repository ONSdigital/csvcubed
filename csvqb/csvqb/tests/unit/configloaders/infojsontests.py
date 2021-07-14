import unittest
import pandas as pd
from dateutil import parser


from csvqb.writers.qbwriter import write_metadata
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

    def test_multiple_measures_and_units_loaded_in_uri_template(self):
        """
        bottles-data.csv has multiple measures and multiple units

        The JSON schema for the info.json files which defines all of the possible properties an info.json can have is
        to be found at <https://github.com/GSS-Cogs/family-schemas/blob/main/dataset-schema.json>.
        """

        data = pd.read_csv(self.get_test_cases_dir() / "configloaders" / "bottles-test-files" / "bottles-data.csv")
        cube = get_cube_from_info_json(
            self.get_test_cases_dir() / "configloaders" / "bottles-test-files" / "bottles-info.json",
            data)

        """Measure URI"""

        expected_measure_uris = ['http://gss-data.org.uk/def/x/one-litre-and-less',
                                 'http://gss-data.org.uk/def/x/more-than-one-litre',
                                 'http://gss-data.org.uk/def/x/number-of-bottles']
        measure_column = cube.columns[1]

        self.assertIsInstance(measure_column, QbColumn)
        self.assertIsInstance(measure_column.component, QbMultiMeasureDimension)

        # [str(c) for c in cube.columns]

        actual_measure_uris = [x.measure_uri for x in measure_column.component.measures]
        self.assertCountEqual(expected_measure_uris, actual_measure_uris)

        """Unit URI"""

        unit_column = cube.columns[2]

        self.assertIsInstance(unit_column, QbColumn)
        self.assertIsInstance(unit_column.component, QbMultiUnits)

        expected_unit_uris = ['http://gss-data.org.uk/def/concept/measurement-units/count',
                              'http://gss-data.org.uk/def/concept/measurement-units/percentage']

        actual_unit_uris = [x.unit_uri for x in unit_column.component.units]
        self.assertCountEqual(expected_unit_uris, actual_unit_uris)

        errors = cube.validate()
        errors += validate_qb_component_constraints(cube)

        self.assert_no_validation_errors(errors)

    def test_cube_metadata_extracted_from_info_json(self):

        """Metadata - ['base_uri', 'creator', 'description', 'from_dict', 'issued', 'keywords', 'landing_page', 
        'license', 'public_contact_point', 'publisher', 'summary', 'themes', 'title', 
        'uri_safe_identifier', 'validate']"""

        data = pd.read_csv(self.get_test_cases_dir() / "configloaders" / "bottles-test-files" / "bottles-data.csv")
        cube = get_cube_from_info_json(
            self.get_test_cases_dir() / "configloaders" / "bottles-test-files" / "bottles-info.json",
            data)

        # Creator - pass

        expected_creator = "HM Revenue & Customs"
        actual_creator = cube.metadata.creator
        self.assertEqual(expected_creator, actual_creator)

        # Description - pass

        expected_description = "All bulletins provide details on percentage of one litre or less & more than " \
                               "one litre bottles. This information is provided on a yearly basis."
        actual_description = cube.metadata.description
        self.assertEqual(expected_description, actual_description)

        # issue_date - pass

        expected_issued_date = parser.parse("2019-02-28")
        actual_issued_date = cube.metadata.issued
        self.assertEqual(actual_issued_date, expected_issued_date)

        # keywords - pass
        # There's currently no `keywords` property to map from the info.json.
        expected_keywords = []
        actual_keywords = cube.metadata.keywords
        self.assertEqual(expected_keywords, actual_keywords)

        # landingpage - pass

        expected_landingpage = "https://www.gov.uk/government/statistics/bottles-bulletin"
        actual_landingpage = cube.metadata.landing_page
        self.assertEqual(expected_landingpage, actual_landingpage)

        # license - pass
        # Surprisingly the info.json schema doesn't allow a licence property just yet.
        expected_license = None
        actual_license = cube.metadata.license
        self.assertEqual(expected_license, actual_license)

        # public_contact_point - pass
        # The info.json schema doesn't allow a public_contact_point property just yet

        expected_public_contact_point = None
        actual_public_contact_point = cube.metadata.public_contact_point
        self.assertEqual(expected_public_contact_point, actual_public_contact_point)

        # publisher - pass

        expected_publisher = "HM Revenue & Customs"
        actual_publisher = cube.metadata.publisher
        self.assertEqual(expected_publisher, actual_publisher)

        # summary - pass
        # The info.json schema doesn't allow a summary property just yet

        expected_summary = None
        actual_summary = cube.metadata.summary
        self.assertEqual(expected_summary, actual_summary)

        # themes - pass
        # It's the families property

        expected_themes = ["Trade"]
        actual_themes = cube.metadata.themes
        self.assertEqual(expected_themes, actual_themes)

        # title - pass

        expected_title = "bottles"
        actual_title = cube.metadata.title
        self.assertEqual(expected_title, actual_title)

        # uri_safe_identifier - pass

        expected_uri_safe_identifier = "bottles-bulletin"
        actual_uri_safe_identifier = cube.metadata.uri_safe_identifier
        self.assertEqual(expected_uri_safe_identifier, actual_uri_safe_identifier)

        errors = cube.validate()
        errors += validate_qb_component_constraints(cube)

        self.assert_no_validation_errors(errors)

if __name__ == '__main__':
    unittest.main()
