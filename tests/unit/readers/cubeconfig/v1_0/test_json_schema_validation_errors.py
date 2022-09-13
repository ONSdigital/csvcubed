import datetime
from pathlib import Path
import json
import pandas as pd
from tempfile import TemporaryDirectory
from typing import List
import re

from csvcubed.models.cube.qb.components.attribute import ExistingQbAttribute
from csvcubed.models.cube.qb.components.codelist import (
    CompositeQbCodeList,
    ExistingQbCodeList,
)
from csvcubed.models.cube.qb.components.concept import DuplicatedQbConcept
from csvcubed.models.cube.qb.components.dimension import ExistingQbDimension
from csvcubed.models.cube.qb.components.measure import ExistingQbMeasure
from csvcubed.models.cube.qb.components.unit import ExistingQbUnit
from csvcubed.readers.catalogmetadata.v1.catalog_metadata_reader import (
    metadata_from_dict,
)

import pytest

from csvcubed.models.cube.cube import Cube
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.components.attributevalue import (
    NewQbAttributeValue,
)
from csvcubed.models.cube.qb.components.observedvalue import (
    QbMultiMeasureObservationValue,
    QbSingleMeasureObservationValue,
)
from csvcubed.readers.cubeconfig.v1.mapcolumntocomponent import (
    map_column_to_qb_component,
)
from csvcubed.utils.iterables import first
from csvcubed.utils.uri import uri_safe
from csvcubed.cli.build import build as cli_build
from csvcubed.readers.cubeconfig.schema_versions import get_deserialiser_for_schema
from csvcubed.readers.cubeconfig.v1.configdeserialiser import _get_qb_column_from_json

from tests.unit.test_baseunit import get_test_cases_dir, assert_num_validation_errors
from csvcubed.definitions import APP_ROOT_DIR_PATH
from csvcubed.models.cube.qb import QbColumn
from csvcubed.models.cube.qb.components import (
    NewQbMeasure,
    NewQbUnit,
    NewQbDimension,
    NewQbCodeList,
    QbMultiMeasureDimension,
    QbMultiUnits,
    NewQbAttribute,
    NewQbConcept,
)

from .virtualconfigs import VirtualConfigurations as vc

TEST_CASE_DIR = get_test_cases_dir().absolute() / "readers" / "cube-config" / "v1.0"


@pytest.mark.vcr
def test_json_schema_license_error_mapping():
    _assert_single_json_schema_validation_error_message(
        TEST_CASE_DIR / "schema_validation_errors" / "license_not_in_enum.json",
        "License 'http://example.com/some-license' is not recognised by csvcubed.",
    )


@pytest.mark.vcr
def test_json_schema_publisher_error_mapping():
    _assert_single_json_schema_validation_error_message(
        TEST_CASE_DIR / "schema_validation_errors" / "publisher_not_in_enum.json",
        "Publisher 'http://example.com/publisher' is not recognised by csvcubed.",
    )


@pytest.mark.vcr
def test_json_schema_creator_error_mapping():
    _assert_single_json_schema_validation_error_message(
        TEST_CASE_DIR / "schema_validation_errors" / "creator_not_in_enum.json",
        "Creator 'http://example.com/creator' is not recognised by csvcubed.",
    )


@pytest.mark.vcr
def test_json_schema_from_existing_dimension_error_mapping():
    error = _assert_single_json_schema_validation_error_message(
        TEST_CASE_DIR
        / "schema_validation_errors"
        / "from_existing_dim_not_in_enum.json",
        "{'type': 'dimension', 'label': 'Trade Direction Dimension', 'code_list': True, 'from_existing': "
        "'http://example.com/dimensions/trade-direction'} is not valid under any of the given schemas",
    )

    existing_dimension_error = first(
        error.context,
        lambda e: e.message
        == "Existing dimension 'http://example.com/dimensions/trade-direction' is not recognised by csvcubed.",
    )
    assert existing_dimension_error is not None


@pytest.mark.vcr
def test_json_schema_from_existing_measure_error_mapping():
    error = _assert_single_json_schema_validation_error_message(
        TEST_CASE_DIR
        / "schema_validation_errors"
        / "from_existing_meas_not_in_enum.json",
        "{'type': 'measures', 'values': [{'label': 'Monetary Value', 'from_existing': "
        "'http://example.com/measure/monetary-value'}]} is not valid under any of the given schemas",
    )

    error_message = error.to_display_string()

    assert error_message == ""
    # existing_dimension_error = first(
    #     error.context,
    #     lambda e: e.message
    #     == "Existing dimension 'http://example.com/dimensions/trade-direction' is not recognised by csvcubed.",
    # )
    # assert existing_dimension_error is not None


def _assert_single_json_schema_validation_error_message(
    config_path: Path, expected_error_message: str
):
    deserialiser = get_deserialiser_for_schema(None)
    csv_path = TEST_CASE_DIR / "schema_validation_errors" / "data.csv"
    _, json_schema_errors, _ = deserialiser(csv_path, config_path)
    assert len(json_schema_errors) == 1
    error = json_schema_errors[0]
    assert error.message == expected_error_message
    return error


if __name__ == "__main__":
    pytest.main()
