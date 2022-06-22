from dataclasses import dataclass
import pytest

from csvcubed.utils.uri import (
    get_last_uri_part,
    csvw_column_name_safe,
    looks_like_uri,
    ensure_looks_like_uri,
    ensure_values_in_lists_looks_like_uris,
    extract_uri_template_variable_name_by_index
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

def test_extract_uri_template_variable_name_by_index():

    @dataclass
    class Case:
        uri: str
        expected: str
        index: int = 0

    for case in [
        Case("http://example.com/something/{+foo}", "foo"),
        Case("http://example.com/something/{foo}", "foo"),
        Case("http://example.com/something/{+foo}/thing/{+bar}", "bar", 1),
        Case("something/{i}{+am}{lots}{+of}{tokens}/something#else{ontheend}", "lots", 2),
        Case("something/{i}{+am}{lots}{+of}{tokens}/something#else{ontheend}", "of", 3),
        Case("something/{i}{+am}{lots}{+of}{tokens}/something#else{ontheend}", "ontheend", 5)
    ]:

        var_got = extract_uri_template_variable_name_by_index(case.uri, case.index)
        assert var_got == case.expected, f'Expected var {case.expected} from {case.uri}, got {var_got}'

if __name__ == "__main__":
    pytest.main()
