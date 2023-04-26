from pathlib import Path

from pandas import DataFrame
from treelib import Tree

from csvcubed.cli.inspectcsvw.inspectdatasetmanager import load_csv_to_dataframe
from csvcubed.utils.skos.codelist import (
    CodelistPropertyUrl,
    build_concepts_hierarchy_tree,
    get_codelist_col_title_by_property_url,
    get_codelist_col_title_from_col_name,
)
from tests.helpers.inspectors_cache import get_code_list_inspector
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"
_test_case_utils_dir = get_test_cases_dir() / "utils"


def test_get_codelist_col_title_by_property_url_label():
    """
    Should return the correct column title for the property URI of type rdfs:label.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "alcohol-content.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(csvw_metadata_json_path)
    primary_catalogue_metadata = (
        code_list_inspector.csvw_inspector.get_primary_catalog_metadata()
    )
    csv_url = code_list_inspector.get_table_identifiers_for_concept_scheme(
        primary_catalogue_metadata.dataset_uri
    ).csv_url

    result_code_list_cols = (
        code_list_inspector.csvw_inspector.get_column_definitions_for_csv(csv_url)
    )
    label_col_name = get_codelist_col_title_by_property_url(
        result_code_list_cols, CodelistPropertyUrl.RDFLabel
    )

    assert label_col_name == "Label"


def test_get_codelist_col_title_by_property_url_notation():
    """
    Should return the correct column title for the property URI of type skos:notation.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "alcohol-content.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(csvw_metadata_json_path)
    primary_catalogue_metadata = (
        code_list_inspector.csvw_inspector.get_primary_catalog_metadata()
    )
    csv_url = code_list_inspector.get_table_identifiers_for_concept_scheme(
        primary_catalogue_metadata.dataset_uri
    ).csv_url

    result_code_list_cols = (
        code_list_inspector.csvw_inspector.get_column_definitions_for_csv(csv_url)
    )

    result_table_schema_properties_for_csv_url = (
        code_list_inspector.csvw_inspector.get_table_info_for_csv_url(csv_url)
    )

    unique_identifier = get_codelist_col_title_from_col_name(
        result_code_list_cols,
        result_table_schema_properties_for_csv_url.primary_key_col_names[0],
    )

    assert unique_identifier == "Notation"


def test_get_codelist_col_title_by_property_url_parent_notation():
    """
    Should return the correct column title for the property URI of type skos:broader.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "alcohol-content.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(csvw_metadata_json_path)
    primary_catalogue_metadata = (
        code_list_inspector.csvw_inspector.get_primary_catalog_metadata()
    )
    csv_url = code_list_inspector.get_table_identifiers_for_concept_scheme(
        primary_catalogue_metadata.dataset_uri
    ).csv_url

    result_code_list_cols = (
        code_list_inspector.csvw_inspector.get_column_definitions_for_csv(csv_url)
    )

    parent_notation_col_name = get_codelist_col_title_by_property_url(
        result_code_list_cols, CodelistPropertyUrl.SkosBroader
    )

    assert parent_notation_col_name == "Parent Notation"


def test_get_codelist_col_title_by_property_url_sort_priority():
    """
    Should return the correct column title for the property URI of type rdfs:label.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "alcohol-content.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(csvw_metadata_json_path)
    primary_catalogue_metadata = (
        code_list_inspector.csvw_inspector.get_primary_catalog_metadata()
    )
    csv_url = code_list_inspector.get_table_identifiers_for_concept_scheme(
        primary_catalogue_metadata.dataset_uri
    ).csv_url

    result_code_list_cols = (
        code_list_inspector.csvw_inspector.get_column_definitions_for_csv(csv_url)
    )

    sort_priority_col_name = get_codelist_col_title_by_property_url(
        result_code_list_cols, CodelistPropertyUrl.SortPriority
    )

    assert sort_priority_col_name == "Sort Priority"


def test_get_codelist_col_title_by_property_url_rdfs_comment():
    """
    Should return the correct column title for the property URI of type rdfs:label.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "alcohol-content.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(csvw_metadata_json_path)
    primary_catalogue_metadata = (
        code_list_inspector.csvw_inspector.get_primary_catalog_metadata()
    )
    csv_url = code_list_inspector.get_table_identifiers_for_concept_scheme(
        primary_catalogue_metadata.dataset_uri
    ).csv_url

    result_code_list_cols = (
        code_list_inspector.csvw_inspector.get_column_definitions_for_csv(csv_url)
    )
    comment_col_name = get_codelist_col_title_by_property_url(
        result_code_list_cols, CodelistPropertyUrl.RDFsComment
    )

    assert comment_col_name == "Description"


def test_get_codelist_col_title_by_property_url_rdfs_type():
    """
    Should return the correct column title for the property URI of type rdfs:label.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "alcohol-content.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(csvw_metadata_json_path)
    primary_catalogue_metadata = (
        code_list_inspector.csvw_inspector.get_primary_catalog_metadata()
    )
    csv_url = code_list_inspector.get_table_identifiers_for_concept_scheme(
        primary_catalogue_metadata.dataset_uri
    ).csv_url

    result_code_list_cols = (
        code_list_inspector.csvw_inspector.get_column_definitions_for_csv(csv_url)
    )

    type_col_name = get_codelist_col_title_by_property_url(
        result_code_list_cols, CodelistPropertyUrl.RDFType
    )

    assert type_col_name is None


def test_build_concepts_hierarchy_tree_of_depth_one():
    """
    Should return the expected Tree for the concepts with hierarchical depth of one.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "alcohol-content.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(csvw_metadata_json_path)
    primary_catalogue_metadata = (
        code_list_inspector.csvw_inspector.get_primary_catalog_metadata()
    )
    csv_url = code_list_inspector.get_table_identifiers_for_concept_scheme(
        primary_catalogue_metadata.dataset_uri
    ).csv_url

    result_code_list_cols = (
        code_list_inspector.csvw_inspector.get_column_definitions_for_csv(csv_url)
    )
    dataset: DataFrame = load_csv_to_dataframe(csvw_metadata_json_path, Path(csv_url))

    parent_notation_col_name = get_codelist_col_title_by_property_url(
        result_code_list_cols, CodelistPropertyUrl.SkosBroader
    )
    unique_identifier = get_codelist_col_title_by_property_url(
        result_code_list_cols, CodelistPropertyUrl.SkosNotation
    )
    label_col_name = get_codelist_col_title_by_property_url(
        result_code_list_cols, CodelistPropertyUrl.RDFLabel
    )
    concepts_tree = build_concepts_hierarchy_tree(
        dataset, parent_notation_col_name, label_col_name, unique_identifier
    )

    assert isinstance(concepts_tree, Tree)
    assert concepts_tree.depth() == 1
    assert len(concepts_tree.all_nodes_itr()) == 7


def test_build_concepts_hierarchy_tree_of_depth_more_than_one():
    """
    Should return the expected Tree for the concepts with hierarchical depth of more than one.
    """
    csvw_metadata_json_path = _test_case_base_dir / "itis-industry.csv-metadata.json"
    code_list_inspector = get_code_list_inspector(csvw_metadata_json_path)
    primary_catalogue_metadata = (
        code_list_inspector.csvw_inspector.get_primary_catalog_metadata()
    )
    csv_url = code_list_inspector.get_table_identifiers_for_concept_scheme(
        primary_catalogue_metadata.dataset_uri
    ).csv_url

    result_code_list_cols = (
        code_list_inspector.csvw_inspector.get_column_definitions_for_csv(csv_url)
    )
    dataset: DataFrame = load_csv_to_dataframe(csvw_metadata_json_path, Path(csv_url))

    parent_notation_col_name = get_codelist_col_title_by_property_url(
        result_code_list_cols, CodelistPropertyUrl.SkosBroader
    )
    unique_identifier = get_codelist_col_title_by_property_url(
        result_code_list_cols, CodelistPropertyUrl.SkosNotation
    )
    label_col_name = get_codelist_col_title_by_property_url(
        result_code_list_cols, CodelistPropertyUrl.RDFLabel
    )
    concepts_tree = build_concepts_hierarchy_tree(
        dataset, parent_notation_col_name, label_col_name, unique_identifier
    )

    assert isinstance(concepts_tree, Tree)
    assert concepts_tree.depth() == 2
    assert len(concepts_tree.all_nodes_itr()) == 10
