import pytest
from pathlib import Path

from csvcubed.utils.sparql import path_to_file_uri_for_rdflib


def test_path_to_file_uri_for_rdflib():
    windows_path_uri = path_to_file_uri_for_rdflib(Path("C:\\Users\\someone\\Code\\something"))
    assert windows_path_uri == "file://C:/Users/someone/Code/something"

    unix_path_uri = path_to_file_uri_for_rdflib(Path("/home/someone/Code/something"))
    assert unix_path_uri == "file:///home/someone/Code/something"

if __name__ == "__main__":
    pytest.main()
