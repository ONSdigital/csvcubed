from pprint import pprint as pp

import pytest

from csvcubed.inspect.inspect_api import CodeListTable, CsvWBrowser, DataCubeTable
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "inspect"


def test_csvwbrowser():
    csvw_metadata_json_path = (
        _test_case_base_dir / "anxiety" / "anxiety.csv-metadata.json"
    )
    anxiety_browser = CsvWBrowser(csvw_metadata_json_path)
    anxiety_tables = anxiety_browser.tables
    for table in anxiety_tables:
        if isinstance(table, DataCubeTable):
            for column_name, column_contents in table.columns.items():
                pp(f"{column_name}: {column_contents.info.column_definition}")
        elif isinstance(table, CodeListTable):
            pp(table.concept_scheme_uri)
    anxiety_table = anxiety_tables[0]
    pp(anxiety_tables)
    pp(anxiety_table.columns)
    assert isinstance(anxiety_table, DataCubeTable)


# eurovision_browser = CsvWBrowser(
#     "~/Code/csvcubed-demo/sweden_at_eurovision_full/out/sweden-at-eurovision-complete-dataset.csv-metadata.json"
# )

# eurovision_table = eurovision_browser.tables[0]
# assert isinstance(eurovision_table, DataCubeTable)


# from pprint import pp


# pp(eurovision_browser.tables)
# pp(eurovision_table.columns)
