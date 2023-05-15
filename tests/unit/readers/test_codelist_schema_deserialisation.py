import inspect

import pytest

from csvcubed.readers.codelistconfig.codelist_schema_versions import (
    LATEST_CODELIST_SCHEMA_URL,
    CodeListConfigJsonSchemaMajorVersion,
    CodeListConfigJsonSchemaMinorVersion,
    _extract_and_validate_code_list_v1,
    _get_code_list_schema_version,
    get_code_list_versioned_deserialiser,
    get_deserialiser_for_code_list_schema,
)
from tests.unit.test_baseunit import get_test_cases_dir


def test_get_code_list_schema_version_1_0():
    """Test checking if the correct schema version is returned for the v1.0 schema"""
    (major, minor) = _get_code_list_schema_version(
        "https://purl.org/csv-cubed/code-list-config/v1.0"
    )

    assert major == CodeListConfigJsonSchemaMajorVersion.v1
    assert minor == CodeListConfigJsonSchemaMinorVersion.v0


def test_get_code_list_schema_version_1_1():
    """Test checking if the correct schema version is returned for the v1.1 schema"""
    (major, minor) = _get_code_list_schema_version(
        "https://purl.org/csv-cubed/code-list-config/v1.1"
    )

    assert major == CodeListConfigJsonSchemaMajorVersion.v1
    assert minor == CodeListConfigJsonSchemaMinorVersion.v1


def test_get_code_list_schema_version_1_2():
    """Test checking if the correct schema version is returned for the v1.2 schema"""
    (major, minor) = _get_code_list_schema_version(
        "https://purl.org/csv-cubed/code-list-config/v1.2"
    )

    assert major == CodeListConfigJsonSchemaMajorVersion.v1
    assert minor == CodeListConfigJsonSchemaMinorVersion.v2


def test_get_code_list_schema_version_1_latest():
    """Test checking if incase the version number doesn't contain a minor it will return the latest schema version
    Note: This will have to be updated when a newer version is added!
    """

    (major, minor) = _get_code_list_schema_version(
        "https://purl.org/csv-cubed/code-list-config/v1"
    )

    assert major == CodeListConfigJsonSchemaMajorVersion.v1
    assert minor == CodeListConfigJsonSchemaMinorVersion.v2


def test_get_code_list_schema_version_error():
    """Testing when the Schema version is not valid the correct ValueError is thrown with the correct error message."""
    with pytest.raises(ValueError) as exception:
        (major, minor) = _get_code_list_schema_version(
            "https://purl.org/csv-cubed/code-list-config/doesmt-exist"
        )
    assert (
        str(exception.value)
        == "The $schema 'https://purl.org/csv-cubed/code-list-config/doesmt-exist' referenced in the code list config file is not recognised. Please check for any updates to your csvcubed installation."
    )


def test_get_deserialiser_for_code_list_schema():
    """Testing when the correct Schema version is passed in it will call the correct function and return
    a CodeListConfigDeserialiser(Tuple[NewQbCodeList, List[JsonSchemaValidationError], List[ValidationError]]).
    Note: The function assertion cannot be triggered. The _get_code_list_schema_version assertion will flag the error before.
    """
    code_list_config_deserialiser = get_deserialiser_for_code_list_schema(
        "https://purl.org/csv-cubed/code-list-config/v1.2",
        default_schema_uri=LATEST_CODELIST_SCHEMA_URL,
    )

    # Let's check that it ends up calling the v1 deserialiser function, dodgy code ahead:
    assert _extract_and_validate_code_list_v1.__name__ in inspect.getsource(
        code_list_config_deserialiser
    )


def test_get_deserialiser_for_code_list_schema_dict():
    """Testing get_code_list_versioned_deserialiser does get the correct deserialiser
    when it is provided with a dict and not a PATH.
    """
    code_list = {"$schema": "https://purl.org/csv-cubed/code-list-config/v1.2"}

    code_list_config_deserialiser = get_code_list_versioned_deserialiser(
        code_list,
        default_schema_uri=LATEST_CODELIST_SCHEMA_URL,
    )

    # Let's check that it ends up calling the v1 deserialiser function, dodgy code ahead:
    assert _extract_and_validate_code_list_v1.__name__ in inspect.getsource(
        code_list_config_deserialiser
    )
