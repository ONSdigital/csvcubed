from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List

import pandas as pd

from csvcubed.cli.buildcsvw.build import build_csvw as cli_build
from csvcubed.models.codelistconfig.code_list_config import (
    CODE_LIST_CONFIG_DEFAULT_URL,
    CodeListConfig,
    CodeListConfigConcept,
)
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.components.codelist import NewQbCodeList
from csvcubed.models.cube.qb.components.concept import DuplicatedQbConcept, NewQbConcept
from csvcubed.utils.datetime import parse_iso_8601_date_time
from csvcubed.utils.dict import get_with_func_or_none
from csvcubed.writers.skoscodelistwriter import SkosCodeListWriter
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_readers_base_dir = (
    get_test_cases_dir() / "readers" / "code-list-config" / "v1.0"
)
_test_case_writers_base_dir = get_test_cases_dir() / "writers"


def _assert_code_list_config_concepts(
    concepts: List[CodeListConfigConcept], concepts_jsons: List[Dict]
):
    """
    Asserts the concepts data provided in the code list config.
    """
    for concept in concepts:
        for concept_json in concepts_jsons:
            if concept.notation == concept_json["notation"]:
                assert concept.label == concept_json["label"]
                assert concept.description == concept_json["description"]
                assert concept.notation == concept_json["notation"]
                if concept.exact_match:
                    assert concept.exact_match == concept_json["same_as"]
                if concept.children:
                    _assert_code_list_config_concepts(
                        concept.children, concept_json["children"]
                    )
                if concept.uri_safe_identifier_override:
                    assert (
                        concept.uri_safe_identifier_override
                        == concept_json["uri_safe_identifier_override"]
                    )


def _assert_code_list_concept_sorting(
    concepts: List[CodeListConfigConcept], expected_sort_orders: Dict
):
    """
    Asserts the sort order of concepts.
    """
    for concept in concepts:
        assert expected_sort_orders.get(concept.notation) == concept.sort_order


def _assert_code_list_config_data(
    code_list_config: CodeListConfig, code_list_config_json: Dict
):
    """
    Asserts the catalog meta data provided in code list config.
    """
    assert code_list_config.sort.by == code_list_config_json["sort"]["by"]
    assert code_list_config.sort.method == code_list_config_json["sort"]["method"]
    assert code_list_config.metadata.title == code_list_config_json["title"]
    assert code_list_config.metadata.description == code_list_config_json["description"]
    assert code_list_config.metadata.summary == code_list_config_json["summary"]
    assert code_list_config.metadata.creator_uri == code_list_config_json["creator"]
    assert code_list_config.metadata.publisher_uri == code_list_config_json["publisher"]
    assert code_list_config.metadata.dataset_issued == get_with_func_or_none(
        code_list_config_json, "dataset_issued", parse_iso_8601_date_time
    )
    assert code_list_config.metadata.dataset_modified == get_with_func_or_none(
        code_list_config_json, "dataset_modified", parse_iso_8601_date_time
    )
    assert code_list_config.metadata.license_uri == code_list_config_json["license"]
    assert len(code_list_config.metadata.theme_uris) == len(
        code_list_config_json["themes"]
    )
    assert code_list_config.metadata.theme_uris[0] == code_list_config_json["themes"][0]
    assert len(code_list_config.metadata.keywords) == len(
        code_list_config_json["keywords"]
    )
    assert code_list_config.metadata.keywords[0] == code_list_config_json["keywords"][0]


def test_code_list_config():
    """
    Should return CodeListConfig for config json path.
    """
    code_list_config_json_path = (
        _test_case_readers_base_dir / "code_list_config_none_hierarchical.json"
    )
    code_list_config, code_list_config_json = CodeListConfig.from_json_file(
        Path(code_list_config_json_path)
    )

    assert code_list_config.schema == code_list_config_json["$schema"]
    _assert_code_list_config_data(code_list_config, code_list_config_json)
    _assert_code_list_config_concepts(
        code_list_config.concepts, code_list_config_json["concepts"]
    )
    _assert_code_list_concept_sorting(
        code_list_config.concepts,
        expected_sort_orders={"a": 2, "b": 3, "c": 1, "d": 4, "e": 0},
    )


def test_code_list_config_without_schema():
    """
    Should return CodeListConfig for config json path.
    """
    code_list_config_json_path = (
        _test_case_readers_base_dir
        / "code_list_config_none_hierarchical_without_schema.json"
    )
    code_list_config, code_list_config_json = CodeListConfig.from_json_file(
        Path(code_list_config_json_path)
    )

    assert code_list_config.schema == CODE_LIST_CONFIG_DEFAULT_URL
    _assert_code_list_config_data(code_list_config, code_list_config_json)
    _assert_code_list_config_concepts(
        code_list_config.concepts, code_list_config_json["concepts"]
    )
    _assert_code_list_concept_sorting(
        code_list_config.concepts,
        expected_sort_orders={"a": 0, "b": 1, "c": 2, "d": 3, "e": 4},
    )


def test_code_list_config_with_hierarchy():
    """
    Should return CodeListConfig for config json path.
    """

    code_list_config_json_path = (
        _test_case_readers_base_dir / "code_list_config_hierarchical.json"
    )
    code_list_config, code_list_config_json = CodeListConfig.from_json_file(
        Path(code_list_config_json_path)
    )

    assert code_list_config.schema == code_list_config_json["$schema"]
    _assert_code_list_config_data(code_list_config, code_list_config_json)
    _assert_code_list_config_concepts(
        code_list_config.concepts, code_list_config_json["concepts"]
    )
    _assert_code_list_concept_sorting(
        code_list_config.concepts,
        expected_sort_orders={"a": 1, "b": 0, "c": 2, "d": 0, "e": 0},
    )


def test_code_list_config_with_concepts_defined_elsewhere():
    """
    Should return CodeListConfig for config json path.
    """

    code_list_config_json_path = (
        _test_case_readers_base_dir
        / "code_list_config_with_concepts_defined_elsewhere.json"
    )
    code_list_config, code_list_config_json = CodeListConfig.from_json_file(
        Path(code_list_config_json_path)
    )

    assert code_list_config.schema == code_list_config_json["$schema"]
    _assert_code_list_config_data(code_list_config, code_list_config_json)
    _assert_code_list_config_concepts(
        code_list_config.concepts, code_list_config_json["concepts"]
    )
    _assert_code_list_concept_sorting(
        code_list_config.concepts,
        expected_sort_orders={"a": 1, "b": 0, "c": 2, "d": 0, "e": 0},
    )


def test_should_detect_duplicated_concepts():
    """
    Should return true as duplicated concepts are defined.
    """

    code_list = NewQbCodeList(
        CatalogMetadata("Some CodeList"),
        [
            NewQbConcept(
                label="Wales",
                code="wales",
            ),
            DuplicatedQbConcept(
                existing_concept_uri="http://data.europa.eu/nuts/code/UKM",
                label="Scotland",
                code="scotland",
            ),
        ],
    )

    writer = SkosCodeListWriter(code_list)
    assert writer.has_duplicated_qb_concepts(code_list) == True


def test_should_not_detect_duplicated_concepts():
    """
    Should return false as no duplicated concepts are defined.
    """

    code_list = NewQbCodeList(
        CatalogMetadata("Some CodeList"),
        [
            NewQbConcept(
                label="Wales",
                code="wales",
            ),
            NewQbConcept(
                label="Scotland",
                code="scotland",
            ),
        ],
    )

    writer = SkosCodeListWriter(code_list)
    assert writer.has_duplicated_qb_concepts(code_list) == False


def test_same_as_field_in_output_csv():
    """
    The output csv should contain existing concept uri when the concepts has the same as field defined.
    And whether the expected uris are present in the column.
    """
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output_dir = temp_dir / "out"
        config_path = (
            _test_case_writers_base_dir / "skoscodelistwriter" / "colourconfig.json"
        )
        csv_path = _test_case_writers_base_dir / "skoscodelistwriter" / "colours.csv"

        cli_build(
            output_directory=output_dir, csv_path=csv_path, config_path=config_path
        )

        output_df = pd.read_csv(output_dir / "colours.csv")

        assert "Original Concept URI" in output_df.columns

        assert output_df.iloc[0]["Original Concept URI"] == "http://example.org/red"
