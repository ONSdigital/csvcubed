import pytest
from pathlib import PosixPath, WindowsPath
import os

from csvcubed.utils.sparql import path_to_file_uri_for_rdflib


def test_path_to_file_uri_for_rdflib():

    if os.name == "nt":
        windows_path_uri = path_to_file_uri_for_rdflib(
            WindowsPath("C:\\Users\\someone\\Code\\something")
        )
        assert windows_path_uri == "file://C:/Users/someone/Code/something"
    elif os.name == "posix":
        unix_path_uri = path_to_file_uri_for_rdflib(
            PosixPath("/home/someone/Code/something")
        )
        assert unix_path_uri == "file:///home/someone/Code/something"
    else:
        raise Exception(f"Unhandled OS type {os.name}")


def test_path_to_file_uri_for_rdflib_normalisation():
    """
    Test that paths are normalised by `path_to_file_uri_for_rdflib`
    """
    if os.name == "nt":
        windows_path_uri = path_to_file_uri_for_rdflib(
            WindowsPath("C:\\Users\\someone\\Code\\somewhere\\..\\somewhere\\something")
        )
        assert windows_path_uri == "file://C:/Users/someone/Code/somewhere/something"
    elif os.name == "posix":
        unix_path_uri = path_to_file_uri_for_rdflib(
            PosixPath("/home/someone/Code/somewhere/../somewhere/something")
        )
        assert unix_path_uri == "file:///home/someone/Code/somewhere/something"
    else:
        raise Exception(f"Unhandled OS type {os.name}")


if __name__ == "__main__":
    pytest.main()
