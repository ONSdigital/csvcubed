import pytest

from csvcubed.utils.pandas import read_csv
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir()

csv_path = (
        _test_case_base_dir / "utils" / "pandas" / "code-list.csv"
    )
    
def test_na_filter_works():
    """
    running the 'read_csv' command and checking that some of the default na-values
    don't get transformed to NaN values.
    """
    pd_table = read_csv(csv_path)
    assert "nan" in pd_table['Description'].values
    assert "null" in pd_table['Description'].values
    assert "#N/A" not in pd_table['Description'].values
    assert "null"  not in pd_table['Parent Notation'].values
    assert "NULL" in pd_table['Parent Notation'].values
    assert "-nan" in pd_table['Parent Notation'].values
    assert "" not in pd_table
    assert "" not in pd_table['Parent Notation'].values
    assert "" not in pd_table['Description'].values
    assert not pd_table['Parent Notation'].isnull().values.any()

def test_empty_strings_are_replaced_with_NaN():
    """
    Checking to see that zero-length string (i.e. ,,) are translated into NaN
    """
    pd_table = read_csv(csv_path)
    assert pd_table['Description'].isnull().values.any()
    assert pd_table['Description'].isnull().sum() == 13

def test_NaN_value_in_Parent_Notation_column_is_not_typr_string():
    """
    Checking to see that string NaN values (i.e. "NaN") typed into 
    csvs is not treated as a none cell item type value, instead 
    treated as a string type value.
    """
    pd_table = read_csv(csv_path)
    assert not pd_table['Parent Notation'].isnull().values.any()
    assert not pd_table['Parent Notation'].isnull().sum() == 1
    assert "NaN" in pd_table['Parent Notation'].values

if __name__ == "__main__":
    pytest.main()