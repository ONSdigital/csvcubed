import pytest
from pathlib import Path

from csvcubed.utils.pandas_na_filter import refiltered_pandas_read_csv

csv_path = "/workspaces/csvcubed/csvcubed/tests/test-cases/utils/pandas_na_filter/code-list.csv"

def test_na_filter_works():
    pd_table = refiltered_pandas_read_csv(csv_path)
    assert "nan" in pd_table['Description'].values
    assert "null" in pd_table['Description'].values
    assert "#N/A" not in pd_table['Description'].values
    assert "null"  not in pd_table['Parent Notation'].values
    assert "NULL" in pd_table['Parent Notation'].values
    assert "-nan" in pd_table['Parent Notation'].values
    assert "" not in pd_table
    assert "" not in pd_table["Parent Notation"].values
    assert "" not in pd_table["Description"].values
    assert "NaN" not in pd_table["Parent Notation"].values

def test_empty_strings_are_replaced_with_hello():
    pd_table = refiltered_pandas_read_csv(csv_path)
    assert "NaN" not in pd_table["Description"].values
    pd_table = pd_table.fillna("hello")
    assert "hello" in pd_table["Description"].values

if __name__ == "__main__":
    pytest.main()