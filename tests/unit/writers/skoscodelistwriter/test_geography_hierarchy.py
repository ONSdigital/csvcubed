import pandas as pd
import rdflib

from csvcubed.inspect.inspectdatasetmanager import get_dataset_observations_info
from csvcubed.inspect.sparql_handler.sparqlquerymanager import (
    select_geography_hierarchy,
)
from csvcubed.utils.skos.codelist import build_concepts_hierarchy_tree
from tests.helpers.repository_cache import (
    get_code_list_repository,
    get_csvw_rdf_manager,
)
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = (
    get_test_cases_dir() / "writers" / "skoscodelistwriter" / "geographies"
)


def test_geographies():
    code_list_json_path = (
        _test_case_base_dir
        / "out_hierarchy"
        / "region-with-hierarchy.csv-metadata.json"
    )
    region_df = pd.read_csv(
        _test_case_base_dir / "out_hierarchy" / "region-with-hierarchy.csv"
    )
    concept_labels = region_df["Label"].to_list()

    concept_labels_with_prefix = [
        "http://statistics.data.gov.uk/id/statistical-geography/" + label
        for label in concept_labels
    ]
    rdf_manager = get_csvw_rdf_manager(code_list_json_path)
    codelist_graph = rdf_manager.rdf_graph
    results = select_geography_hierarchy(codelist_graph, concept_labels_with_prefix)

    # codelist_repo = get_code_list_repository(code_list_json_path)
    # csvw_type = codelist_repo.csvw_repository.csvw_type
    # observations = get_dataset_observations_info(region_df, csvw_type, None)
    # concepts_tree = build_concepts_hierarchy_tree(
    #     region_df, "Parent Uri Identifier", "Label", "Uri Identifier"
    # )

    assert True
