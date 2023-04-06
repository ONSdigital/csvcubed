import os
from pathlib import Path, PosixPath, WindowsPath

import pytest

from csvcubed.utils.uri import (
    csvw_column_name_safe,
    ensure_looks_like_uri,
    ensure_values_in_lists_looks_like_uris,
    file_uri_to_path,
    get_last_uri_part,
    looks_like_uri,
)


def test_uri_last_part():
    assert "dataset-name#something" == get_last_uri_part(
        "http://gss-data.org.uk/data/stuff/dataset-name#something"
    )


def test_csvw_column_name():
    assert "some_random_column_name" == csvw_column_name_safe(
        "Some Random Column //+Name"
    )
    assert "something_else" == csvw_column_name_safe("Something-else")


def test_looks_like_uri():
    assert looks_like_uri("https://some-domain.org")
    assert looks_like_uri("http://some-domain.org/some-stuff/other-stuff")
    assert looks_like_uri("ftp://some-domain.org")
    assert looks_like_uri("somescheme:somevalue")
    assert looks_like_uri("urn:")

    assert not looks_like_uri("somevalue/cheese")
    assert not looks_like_uri("\\\\server\\temp.txt")

    assert not looks_like_uri("c:\\temp\\temp.txt")
    assert not looks_like_uri("C:\\")
    assert not looks_like_uri("c:/temp/temp.txt")
    assert not looks_like_uri("c:/")


def test_ensure_looks_like_uri():
    ensure_looks_like_uri("http://some-domain.org/")

    with pytest.raises(ValueError) as err:
        ensure_looks_like_uri("not-like-a-uri")

    assert "'not-like-a-uri' does not look like a URI" in str(err)


def test_ensure_all_look_like_uri():
    ensure_values_in_lists_looks_like_uris(
        ["http://some-domain.org/", "http://some-other-domain.org/"]
    )


def test_get_absolute_file_path():
    """
    Testing the URI util function `get_absolute_file_path()` returns a normalised
    path from a string URI which can be used to locate resources on windows as
    well as unix/linux operating systems.
    """
    if os.name == "nt":
        windows_csv_url = "file:\C:\\Users\\someone\\Code\\something"
        absolute_csv_url = file_uri_to_path(windows_csv_url)
        assert isinstance(absolute_csv_url, Path)
        assert absolute_csv_url == WindowsPath("C:/Users/someone/Code/something")
    elif os.name == "posix":
        unix_csv_url = "file:///workspaces/csvcubed/tests/test-cases/cli/inspect/inspector-load-dataframe/pivoted-shape/pivoted-shape-out/testing-converting-a-pivoted-csvw-to-pandas-dataframe.csv"
        absolute_csv_url = file_uri_to_path(unix_csv_url)
        assert isinstance(absolute_csv_url, Path)
        assert absolute_csv_url == PosixPath(
            "/workspaces/csvcubed/tests/test-cases/cli/inspect/inspector-load-dataframe/pivoted-shape/pivoted-shape-out/testing-converting-a-pivoted-csvw-to-pandas-dataframe.csv"
        )


if __name__ == "__main__":
    pytest.main()
