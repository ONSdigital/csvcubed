import os
from pathlib import PosixPath, WindowsPath

import pytest
import rdflib

from csvcubed.models.sparql.valuesbinding import ValuesBinding
from csvcubed.utils.sparql_handler.sparql import path_to_file_uri_for_rdflib, select


def test_path_to_file_uri_for_rdflib():

    if os.name == "nt":
        windows_path_uri = path_to_file_uri_for_rdflib(
            WindowsPath("C:\\Users\\someone\\Code\\something")
        )
        assert windows_path_uri == "file:///C:/Users/someone/Code/something"
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
        assert windows_path_uri == "file:///C:/Users/someone/Code/somewhere/something"
    elif os.name == "posix":
        unix_path_uri = path_to_file_uri_for_rdflib(
            PosixPath("/home/someone/Code/somewhere/../somewhere/something")
        )
        assert unix_path_uri == "file:///home/someone/Code/somewhere/something"
    else:
        raise Exception(f"Unhandled OS type {os.name}")


def test_values_binding():
    """
    Ensure that we can append `ValuesBinding` objects to the end of a SPARQL query to
    provide a set of variables with a table of values.
    """

    results = select(
        """
            SELECT ?a ?b ?c
            WHERE {} 
        """,
        rdflib.Graph(),
        values_bindings=[
            ValuesBinding(
                variable_names=["a", "b", "c"],
                rows=[
                    [
                        rdflib.Literal(1),
                        rdflib.Literal(2),
                        rdflib.Literal(3),
                    ],
                    [
                        rdflib.Literal(4),
                        rdflib.Literal(5),
                        rdflib.Literal(6),
                    ],
                ],
            )
        ],
    )

    assert len(results) == 2
    assert results[0].asdict() == {
        "a": rdflib.Literal(1),
        "b": rdflib.Literal(2),
        "c": rdflib.Literal(3),
    }
    assert results[1].asdict() == {
        "a": rdflib.Literal(4),
        "b": rdflib.Literal(5),
        "c": rdflib.Literal(6),
    }


if __name__ == "__main__":
    pytest.main()
