import pytest


from csvqb.tests.unit.test_baseunit import *
from csvqb.utils.uri import get_last_uri_part, csvw_column_name_safe


def test_uri_last_part():
    assert "dataset-name#something" == get_last_uri_part(
        "http://gss-data.org.uk/data/stuff/dataset-name#something"
    )


def test_csvw_column_name():
    assert "some_random_column_name" == csvw_column_name_safe(
        "Some Random Column //+Name"
    )
    assert "something_else" == csvw_column_name_safe("Something-else")


if __name__ == "__main__":
    pytest.main()
