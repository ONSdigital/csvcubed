from pathlib import Path
from typing import Tuple

import pytest

from csvcubed.readers.codelistconfig.codelist_schema_versions import (
    CodeListConfigJsonSchemaMajorVersion,
    CodeListConfigJsonSchemaMinorVersion,
    _extract_and_validate_code_list_v1,
    _get_schema_code_list_version,
    get_deserialiser_for_code_list_schema,
)
from tests.unit.test_baseunit import get_test_cases_dir


def test_get_schema_code_list_version_1_0():
    """Test checking if the correct schema version is returned for the v1.0 schema"""
    (major, minor) = _get_schema_code_list_version(
        "https://purl.org/csv-cubed/code-list-config/v1.0"
    )

    assert major == CodeListConfigJsonSchemaMajorVersion.v1
    assert minor == CodeListConfigJsonSchemaMinorVersion.v0


def test_get_schema_code_list_version_1_1():
    """Test checking if the correct schema version is returned for the v1.1 schema"""
    (major, minor) = _get_schema_code_list_version(
        "https://purl.org/csv-cubed/code-list-config/v1.1"
    )

    assert major == CodeListConfigJsonSchemaMajorVersion.v1
    assert minor == CodeListConfigJsonSchemaMinorVersion.v1


def test_get_schema_code_list_version_1_latest():
    """Test checking if incase the version number doesn't contain a minor it will return the latest schema version
    Note: This will have to be updated when a newer version is added!
    """

    (major, minor) = _get_schema_code_list_version(
        "https://purl.org/csv-cubed/code-list-config/v1"
    )

    assert major == CodeListConfigJsonSchemaMajorVersion.v1
    assert minor == CodeListConfigJsonSchemaMinorVersion.v1


def test_get_schema_code_list_version_error():
    """Testing when the Schema version is not valid the correct ValueError is thrown with the correct error message."""
    with pytest.raises(ValueError) as exception:
        (major, minor) = _get_schema_code_list_version(
            "https://purl.org/csv-cubed/code-list-config/doesmt-exist"
        )
    assert (
        str(exception.value)
        == "The $schema 'https://purl.org/csv-cubed/code-list-config/doesmt-exist' referenced in the code list config file is not recognised. Please check for any updates to your csvcubed installation."
    )


def test_get_deserialiser_for_code_list_schema():
    """Testsing when the correct Schema version is passed in it will call the correct function and return
    a CodeListConfigDeserialiser(Tuple[NewQbCodeList, List[JsonSchemaValidationError], List[ValidationError]]).
    Note: The function assertion cannot be triggered. The _get_schema_code_list_version assertion will flag the error before.
    """
    code_list_config_deserialiser = get_deserialiser_for_code_list_schema(
        "https://purl.org/csv-cubed/code-list-config/v1.1"
    )
    assert code_list_config_deserialiser == _extract_and_validate_code_list_v1
