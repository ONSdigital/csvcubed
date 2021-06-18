import unittest
from pathlib import Path
import xmlrunner

from pmd.codelist.datetimecodelistgen import \
    _get_dimensions_to_generate_code_lists_for, _get_csv_columns_for_dimension, _get_unique_values_from_columns, \
    _create_code_list_for_dimension, generate_date_time_code_lists_for_csvw_metadata_file

TESTS_ROOT_PATH = Path(".")
TEST_CASES_PATH = TESTS_ROOT_PATH / ".." / "test-cases"

HMRC_OTS_CN8_CSV = TEST_CASES_PATH / "hmrc-overseas-trade-statistics-cn8.csv"
HMRC_OTS_CN8_METADATA_JSON = TEST_CASES_PATH / "hmrc-overseas-trade-statistics-cn8.csv-metadata.json"
HMRC_OTS_CN8_TIME_CODELIST = "http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/" \
                             "hmrc-overseas-trade-statistics-cn8#scheme/period"
HMRC_OTS_CN8_TIME_DIMENSION = "http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/" \
                              "hmrc-overseas-trade-statistics-cn8#dimension/period"
EXPECTED_MONTH_CSV_OUT = TEST_CASES_PATH / "Month.csv"
EXPECTED_MONTH_METADATA_OUT = TEST_CASES_PATH / "Month.csv-metadata.json"


class TestDateTimeCodeListGeneration(unittest.TestCase):
    def test_extracting_date_time_dimensions_from_metadata(self):
        date_time_dimensions = _get_dimensions_to_generate_code_lists_for(HMRC_OTS_CN8_METADATA_JSON)
        self.assertTrue(len(date_time_dimensions) == 1)
        (dimension, label, code_list) = date_time_dimensions[0]
        self.assertEqual(HMRC_OTS_CN8_TIME_DIMENSION, dimension)
        self.assertEqual("Month", label)
        self.assertEqual(HMRC_OTS_CN8_TIME_CODELIST, code_list)

    def test_extracting_columns_for_dimension_from_metadata(self):
        columns = _get_csv_columns_for_dimension(HMRC_OTS_CN8_METADATA_JSON, HMRC_OTS_CN8_TIME_DIMENSION)
        self.assertTrue(len(columns.keys()) == 1)
        expected_csv_files = [k for k in columns.keys() if k.csv_path == HMRC_OTS_CN8_CSV]
        self.assertEqual(1, len(expected_csv_files))
        hmrc_ots_cn8_csv_file = expected_csv_files[0]

        col_names = columns[hmrc_ots_cn8_csv_file]

        self.assertEqual(len(col_names), 1)
        self.assertEqual("period", col_names[0])

    def test_extracting_unique_values_for_dimension(self):
        columns = _get_csv_columns_for_dimension(HMRC_OTS_CN8_METADATA_JSON, HMRC_OTS_CN8_TIME_DIMENSION)
        unique_values = _get_unique_values_from_columns(columns)
        self.assertTrue(len(unique_values) == 3)
        self.assertTrue("http://reference.data.gov.uk/id/month/2020-09" in unique_values)
        self.assertTrue("http://reference.data.gov.uk/id/month/2020-10" in unique_values)
        self.assertTrue("http://reference.data.gov.uk/id/month/2020-11" in unique_values)


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="test-reports"))

