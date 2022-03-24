import pytest

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
    assert "" not in pd_table['Parent Notation'].values
    assert "" not in pd_table['Description'].values
    assert pd_table['Parent Notation'].isnull().values.any()

def test_empty_strings_are_replaced_with_NaN():
    pd_table = refiltered_pandas_read_csv(csv_path)
    assert pd_table['Description'].isnull().values.any()
    assert pd_table['Description'].isnull().sum() == 13

def test_NaN_value_in_Parent_Notation_column_is_not_typr_string():
    pd_table = refiltered_pandas_read_csv(csv_path)
    assert pd_table['Parent Notation'].isnull().values.any()
    assert pd_table['Parent Notation'].isnull().sum() == 1

if __name__ == "__main__":
    pytest.main()