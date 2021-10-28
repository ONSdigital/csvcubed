import pytest
from pathlib import Path

from csvcubedpmd.codelist.datetimecodelistgen import \
    _get_dimensions_to_generate_code_lists_for, _get_csv_columns_for_dimension, _get_unique_values_from_columns

from csvcubeddevtools.behaviour.file import _get_test_cases_dir

TEST_CASES_PATH = _get_test_cases_dir()

HMRC_OTS_CN8_CSV = TEST_CASES_PATH / "hmrc-overseas-trade-statistics-cn8.csv"
HMRC_OTS_CN8_METADATA_JSON = TEST_CASES_PATH / "hmrc-overseas-trade-statistics-cn8.csv-metadata.json"
HMRC_OTS_CN8_TIME_CODELIST = "http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/" \
                             "hmrc-overseas-trade-statistics-cn8#scheme/period"
HMRC_OTS_CN8_TIME_DIMENSION = "http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/" \
                              "hmrc-overseas-trade-statistics-cn8#dimension/period"
EXPECTED_MONTH_CSV_OUT = TEST_CASES_PATH / "Month.csv"
EXPECTED_MONTH_METADATA_OUT = TEST_CASES_PATH / "Month.csv-metadata.json"


def test_extracting_date_time_dimensions_from_metadata():
    date_time_dimensions = _get_dimensions_to_generate_code_lists_for(HMRC_OTS_CN8_METADATA_JSON)
    assert 1 == len(date_time_dimensions)
    (dimension, label, code_list) = date_time_dimensions[0]
    assert HMRC_OTS_CN8_TIME_DIMENSION == dimension
    assert "Month" == label
    assert HMRC_OTS_CN8_TIME_CODELIST == code_list


def test_extracting_columns_for_dimension_from_metadata():
    columns = _get_csv_columns_for_dimension(HMRC_OTS_CN8_METADATA_JSON, HMRC_OTS_CN8_TIME_DIMENSION)
    assert 1 == len(columns.keys())
    expected_csv_files = [k for k in columns.keys() if k.csv_path == HMRC_OTS_CN8_CSV]
    assert 1 == len(expected_csv_files)
    hmrc_ots_cn8_csv_file = expected_csv_files[0]

    col_names = columns[hmrc_ots_cn8_csv_file]

    assert 1 == len(col_names)
    assert "period" == col_names[0]


def test_extracting_unique_values_for_dimension():
    columns = _get_csv_columns_for_dimension(HMRC_OTS_CN8_METADATA_JSON, HMRC_OTS_CN8_TIME_DIMENSION)
    unique_values = _get_unique_values_from_columns(columns)
    assert 3 == len(unique_values)
    assert "http://reference.data.gov.uk/id/month/2020-09" in unique_values
    assert "http://reference.data.gov.uk/id/month/2020-10" in unique_values
    assert "http://reference.data.gov.uk/id/month/2020-11" in unique_values


if __name__ == '__main__':
    pytest.main()
