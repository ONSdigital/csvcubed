"""
CSV-W Helpers
-------------
"""
from pathlib import Path
import csvw


def delete_csvw(metadata_file: Path):
    """
    Deletes a CSV-W metadata file and all referenced CSVs.

    :param metadata_file:
    :return:
    """
    table_group = csvw.TableGroup.from_file(metadata_file)

    tables = table_group.tables
    assert isinstance(tables, list)
    for table in tables:
        assert isinstance(table, csvw.Table)
        if table.url is not None and str(table.url).strip() != "":
            csv_file: Path = metadata_file.parent / str(table.url)
            csv_file.unlink()

    if table_group.url is not None and str(table_group.url).strip() != "":
        csv_file: Path = metadata_file.parent / str(table_group.url)
        csv_file.unlink()

    metadata_file.unlink()
