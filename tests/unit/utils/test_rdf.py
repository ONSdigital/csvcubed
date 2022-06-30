import pytest
import rdflib
from csvcubed.utils.sparql import path_to_file_uri_for_rdflib
from rdflib import URIRef, RDFS, Literal

from csvcubed.utils.rdf import parse_graph_retain_relative
from tests.unit.test_baseunit import get_test_cases_dir


_test_cases_base_dir = get_test_cases_dir() / "utils" / "rdf"


def test_loading_graph_relative_paths():
    """Ensure we can load rdflib graphs whilst retaining relative paths."""
    ttl_path = _test_cases_base_dir / "relative_path.ttl"
    graph_without_relative_paths = rdflib.Graph().parse(ttl_path)
    some_file_path = ttl_path.parent / "some-file.json"
    assert (
        URIRef(
            f"{some_file_path.as_uri()}#some-identifier"
        ),
        RDFS.label,
        Literal("Hello, World", lang="en"),
    ) in graph_without_relative_paths

    graph_with_relative_paths = parse_graph_retain_relative(ttl_path)
    assert (
        URIRef("some-file.json#some-identifier"),
        RDFS.label,
        Literal("Hello, World", lang="en"),
    ) in graph_with_relative_paths


if __name__ == "__main__":
    pytest.main()
