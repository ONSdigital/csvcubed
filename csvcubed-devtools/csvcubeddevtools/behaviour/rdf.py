"""
RDF Test Steps
--------------
"""
from behave import *
from rdflib.compare import to_isomorphic, graph_diff
from rdflib import Graph, ConjunctiveGraph
import distutils.util
from .temporarydirectory import get_context_temp_dir_path

from csvcubeddevtools.helpers import rdflibhelpers


def test_graph_diff(g1, g2):
    in_both, only_in_first, only_in_second = graph_diff(
        to_isomorphic(g1), to_isomorphic(g2)
    )
    only_in_first.namespace_manager = g1.namespace_manager
    only_in_second.namespace_manager = g2.namespace_manager
    assert (
        len(only_in_second) == 0
    ), f"""
        <<<
        {rdflibhelpers.serialise_to_string(only_in_first, format='n3')}
        ===
        {rdflibhelpers.serialise_to_string(only_in_second, format='n3')}
        >>>
        """


@step("the RDF should contain")
def step_impl(context):
    test_graph_diff(
        Graph().parse(format="turtle", data=context.turtle),
        Graph().parse(format="turtle", data=context.text),
    )


@step("the ask query should return {expected_query_result}")
def step_impl(context, expected_query_result: str):
    expected_ask_result = bool(distutils.util.strtobool(expected_query_result))
    assert_ask(context, context.text, expected_ask_result)


def assert_ask(context, ask_query: str, expected_ask_result: bool):
    g = Graph().parse(format="turtle", data=context.turtle)
    results = list(g.query(ask_query))
    ask_result = results[0]
    assert ask_result == expected_ask_result


@given('the N-Quads contained in "{rdf_file}"')
def step_impl(context, rdf_file: str):
    rdf_file_path = get_context_temp_dir_path(context) / rdf_file
    graph = ConjunctiveGraph()
    graph.parse(str(rdf_file_path), format="nquads")
    context.turtle = getattr(context, "turtle", "") + rdflibhelpers.serialise_to_string(
        graph, format="turtle"
    )


@step('the RDF should not contain any instances of "{entity_type}"')
def step_impl(context, entity_type: str):
    query = f"""
        ASK
        WHERE {{
         [] a <{entity_type}>.
        }}
    """

    assert_ask(context, query, False)

@step('the RDF should contain {num_instances:d} instance(s) of "{entity_type}"')
def step_impl(context, num_instances: int, entity_type: str):
    query = f"""
        ASK
        WHERE {{
         ?instance a <{entity_type}>.
        }}
        HAVING (COUNT(DISTINCT ?instance) != {num_instances})
    """

    assert_ask(context, query, False)

@step('the RDF should not contain any URIs in the "{uri_prefix}" namespace')
def step_impl(context, uri_prefix: str):
    query = f"""
        ASK
        WHERE {{
            ?s ?p ?o.
            FILTER(
              strStarts(LCASE(str(?s)), "{uri_prefix}")
                || strStarts(LCASE(str(?p)), "{uri_prefix}")
                || strStarts(LCASE(str(?o)), "{uri_prefix}")
            ).
        }}
    """

    assert_ask(context, query, False)

@step('the RDF should not contain any reference to "{uri}"')
def step_impl(context, uri: str):
    query = f"""
        ASK
        WHERE {{
            ?s ?p ?o.
            FILTER(?s = <{uri}> || ?p = <{uri}> || ?o = <{uri}>).
        }}
    """

    assert_ask(context, query, False)
