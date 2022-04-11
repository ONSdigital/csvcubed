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
    df, _data_errors = read_csv(csv_path)
    assert "nan" in df['Description'].values
    assert "null" in df['Description'].values
    assert "#N/A" in df['Parent Notation'].values
    assert "NULL" in df['Parent Notation'].values
    assert "-nan" in df['Parent Notation'].values
    assert "" not in df
    assert "" not in df['Parent Notation'].values
    assert "" not in df['Description'].values

def test_default_na_values_show_up_in_right_column():
    """
    The original default na values are all entered once between two
    columns "Parent Notation' and 'Description', and we checking that
    they are not converted to NaN values, whilst in the
    correct location in the pandas dataframe.
    """
    df, _data_errors = read_csv(csv_path)
    assert "nan" in df['Description'].values
    assert "nan" not in df['Parent Notation'].values

    assert "null" in df['Description'].values
    assert "null"  not in df['Parent Notation'].values

    assert "#N/A" in df['Parent Notation'].values
    assert "#N/A" not in df['Description'].values

    assert "NULL" in df['Parent Notation'].values
    assert "NULL" not in df['Description'].values

    assert "-nan" in df['Parent Notation'].values
    assert "-nan" not in df['Description'].values

def test_no_NaN_empty_cells_are_in_Parent_Notation_column():
    """
    Original default na values that occupy the entire 'Parent Notation' column
    are not to become NaN values.
    """
    df, _data_errors = read_csv(csv_path)
    assert not df['Parent Notation'].isnull().values.any()


def test_zero_length_strings_are_replaced_with_NaN():
    """
    Checking to see that zero-length string (i.e. ,,) are translated into NaN
    """
    df, _data_errors = read_csv(csv_path)
    assert df['Description'].isnull().values.any()
    assert df['Description'].isnull().sum() == 13


def test_NaN_value_in_Parent_Notation_column_is_type_string():
    """
    Checking to see that string NaN values (i.e. "NaN") typed into 
    csvs is not treated as a none cell item type value, instead 
    treated as a string type value.
    """
    df, _data_errors = read_csv(csv_path)
    assert not df['Parent Notation'].isnull().values.any()
    assert not df['Parent Notation'].isnull().sum() == 1
    assert "NaN" in df['Parent Notation'].values

if __name__ == "__main__":
    pytest.main()