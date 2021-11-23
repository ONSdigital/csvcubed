"""
RDF Test Steps
--------------
"""
from pathlib import Path
from behave import *
from rdflib.compare import to_isomorphic, graph_diff
from rdflib import Graph, Dataset, ConjunctiveGraph
import distutils.util
from .temporarydirectory import get_context_temp_dir_path


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
        {only_in_first.serialize(format='n3').decode('utf-8')}
        ===
        {only_in_second.serialize(format='n3').decode('utf-8')}
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


@given('the RDF contained in "{rdf_file}"')
def step_impl(context, rdf_file: str):
    rdf_file_path = get_context_temp_dir_path(context) / rdf_file
    graph = ConjunctiveGraph()
    graph.parse(str(rdf_file_path), format="nquads")
    context.turtle = getattr(context, "turtle", "") + graph.serialize(
        format="turtle"
    ).decode("utf-8")


@step('the RDF should not contain any instances of "{entity_type}"')
def step_impl(context, entity_type: str):
    query = f"""
        ASK
        WHERE {{
         [] a <{entity_type}>.
        }}
    """

    assert_ask(context, query, False)
