import datetime
import json
import unittest
from pathlib import Path

import pandas as pd
import rdflib

import pmd.models.rdf.pmdcat
from pmd.datetimecodelistgen import \
    _get_dimensions_to_generate_code_lists_for, _get_csv_columns_for_dimension, _get_unique_values_from_columns, \
    _create_code_list_for_dimension

TESTS_ROOT_PATH = Path(".")
TEST_CASES_PATH = TESTS_ROOT_PATH / "test-cases"

HMRC_OTS_CN8_CSV = TEST_CASES_PATH / "hmrc-overseas-trade-statistics-cn8.csv"
HMRC_OTS_CN8_METADATA_JSON = TEST_CASES_PATH / "hmrc-overseas-trade-statistics-cn8.csv-metadata.json"
HMRC_OTS_CN8_TIME_CODELIST = "http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/" \
                             "hmrc-overseas-trade-statistics-cn8#scheme/period"
HMRC_OTS_CN8_TIME_DIMENSION = "http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/" \
                              "hmrc-overseas-trade-statistics-cn8#dimension/period"
EXPECTED_MONTH_CSV_OUT = TEST_CASES_PATH / "Month.csv"
EXPECTED_MONTH_METADATA_OUT = TEST_CASES_PATH / "Month.csv-metadata.json"


class MyTestCase(unittest.TestCase):
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

    def test_code_lists_generated(self):
        date_time_dimensions = _get_dimensions_to_generate_code_lists_for(HMRC_OTS_CN8_METADATA_JSON)
        for (dimension, label, code_list_uri) in date_time_dimensions:
            _create_code_list_for_dimension(HMRC_OTS_CN8_METADATA_JSON, dimension, label, code_list_uri)

        codelist_out = pd.read_csv(EXPECTED_MONTH_CSV_OUT)
        with open(EXPECTED_MONTH_METADATA_OUT, "r") as f:
            codelist_metadata_out = json.load(f)

        # todo: Need some more thorough tests which ensure the validity of the CSV-W metadata + CSV outputted.
        self.assertTrue(False)

    def test_nonsense(self):

        catalog = pmd.models.rdf.pmdcat.Catalog("http://some-catalog")
        catalog.label = catalog.title = catalog.comment = catalog.description = "Catalog"

        ds = pmd.models.rdf.pmdcat.Dataset("http://dataset/1")
        ds.label = ds.comment = ds.title = ds.description = "Nonsense"
        ds.metadata_graph = "http://metadata-graph"
        ds.pmdcat_graph = "http://graph-graph"
        ds.sparql_endpoint = "http://sparql-endpoint"
        ds_contents = ds.dataset_contents = pmd.models.rdf.pmdcat.DatasetContents("http://dataset-contents")
        ds_contents.comment = ds_contents.label = "Dataset contents."

        record_1 = pmd.models.rdf.pmdcat.CatalogRecord("http://some-cat-record/1", "http://some-catalog")
        record_1.label = record_1.title = record_1.comment = record_1.description = "Record 1"
        record_1.issued = datetime.datetime.now()
        record_1.primary_topic = ds
        record_1.metadata_graph = "http://medata-graph"

        record_2 = pmd.models.rdf.pmdcat.CatalogRecord("http://some-cat-record/2", "http://some-catalog")
        record_2.label = record_2.title = record_2.comment = record_2.description = "Record 2"
        record_2.issued = datetime.datetime.now()
        record_2.primary_topic = ds
        record_2.metadata_graph = "http://medata-graph"

        catalog.records.add(record_1)
        catalog.records.add(record_2)
        g = rdflib.Graph()
        catalog.to_graph(g)
        output = g.serialize(format="json-ld")
        self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()

