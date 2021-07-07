from rdflib import Graph


def assert_ask_query(g: Graph, ask_query: str, should_be_true: bool = True) -> None:
    results = g.query(ask_query)
    result: bool = list(results)[0]
    assert result == should_be_true
