from pathlib import Path
from typing import Dict, List

from csvcubed.readers.cubeconfig.utils import load_resource, parse_iso_8601_date_time
from csvcubed.models.codelistconfig.code_list_config import (
    CODE_LIST_CONFIG_DEFAULT_URL,
    CodeListConfig,
    CodeListConfigConcept,
)
from csvcubed.utils.dict import get_with_func_or_none
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "readers" / "code-list-config" / "v1.0"


def _assert_code_list_config_concepts(
    concepts: List[CodeListConfigConcept], concepts_jsons: List[Dict]
):
    """
    Asserts the concepts data provided in the code list config.
    """
    for idx, concept in enumerate(concepts):
        assert concept.label == concepts_jsons[idx]["label"]
        assert concept.description == concepts_jsons[idx]["description"]
        assert concept.notation == concepts_jsons[idx]["notation"]
        if concept.same_as:
            assert concept.same_as == concepts_jsons[idx]["same_as"]
        if concept.children:
            _assert_code_list_config_concepts(
                concept.children, concepts_jsons[idx]["children"]
            )


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


def test_code_list_config_model():
    """
    Should return CodeListConfig for config json path.
    """
    code_list_config_json_path = (
        _test_case_base_dir / "code_list_config_none_hierarchical.json"
    )
    code_list_config, code_list_config_json = CodeListConfig.from_json_file(Path(code_list_config_json_path))

    assert code_list_config.schema == code_list_config_json["$schema"]
    _assert_code_list_config_data(code_list_config, code_list_config_json)
    _assert_code_list_config_concepts(
        code_list_config.concepts, code_list_config_json["concepts"]
    )


def test_code_list_config_model_without_schema():
    """
    Should return CodeListConfig for config json path.
    """
    code_list_config_json_path = (
        _test_case_base_dir / "code_list_config_none_hierarchical_without_schema.json"
    )
    code_list_config, code_list_config_json = CodeListConfig.from_json_file(Path(code_list_config_json_path))

    assert code_list_config.schema == CODE_LIST_CONFIG_DEFAULT_URL
    _assert_code_list_config_data(code_list_config, code_list_config_json)
    _assert_code_list_config_concepts(
        code_list_config.concepts, code_list_config_json["concepts"]
    )


def test_code_list_config_model_with_hierarchy():
    """
    Should return CodeListConfig for config json path.
    """

    code_list_config_json_path = (
        _test_case_base_dir / "code_list_config_hierarchical.json"
    )
    code_list_config, code_list_config_json = CodeListConfig.from_json_file(Path(code_list_config_json_path))

    assert code_list_config.schema == code_list_config_json["$schema"]
    _assert_code_list_config_data(code_list_config, code_list_config_json)
    _assert_code_list_config_concepts(
        code_list_config.concepts, code_list_config_json["concepts"]
    )
