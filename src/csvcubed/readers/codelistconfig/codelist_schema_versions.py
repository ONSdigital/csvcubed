"""
Code List Schema Versions
---------------

Contains an enum listing the code-list-config.json schema versions recognised by csvcubed.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from csvcubed.models.cube.qb.components.codelist import NewQbCodeList
from csvcubed.models.jsonvalidationerrors import JsonSchemaValidationError
from csvcubed.models.validationerror import ValidationError
from csvcubed.readers.cubeconfig.v1 import configdeserialiser as v1_configdeserialiser

_logger = logging.getLogger(__name__)


CodeListConfigDeserialiser = Callable[
    [Path],
    Tuple[NewQbCodeList, List[JsonSchemaValidationError], List[ValidationError]],
]

_v1_0_CODELIST_SCHEMA_URL = "https://purl.org/csv-cubed/code-list-config/v1.0"
_v1_1_CODELIST_SCHEMA_URL = "https://purl.org/csv-cubed/code-list-config/v1.1"

V1_CODELIST_SCHEMA_URL = "https://purl.org/csv-cubed/code-list-config/v1"  # v1 defaults to the latest minor version of v1.*.


_LATEST_V1_CODELSIT_SCHEMA_URL = _v1_1_CODELIST_SCHEMA_URL
"""
    This holds the URL identifying the latest minor version of the V1 schema.

    When adding a new minor version to the V1 schema, you must update this variable.
"""

_LATEST_CODELIST_SCHEMA_URL = _v1_1_CODELIST_SCHEMA_URL
"""
    This holds the URL identifying the latest version of the schema.

    When adding a new schema version, you must update this variable.
"""


class CodeListConfigJsonSchemaMajorVersion(Enum):
    """
    Major versions of the code list config schema.
    """

    v1 = 1


class CodeListConfigJsonSchemaMinorVersion(Enum):
    """
    Minor versions of the code list config schema.
    """

    v0 = 0
    v1 = 1


def get_deserialiser_for_code_list_schema(
    maybe_schema_path: Optional[str],
) -> CodeListConfigDeserialiser:
    """
    Provides a versioned deserialiser function appropriate to the referenced schema.
    """
    # Default to the latest version of the schema.
    schema_path = (
        _LATEST_CODELIST_SCHEMA_URL if maybe_schema_path is None else maybe_schema_path
    )

    schema_version_major, schema_version_minor = _get_schema_code_list_version(
        schema_path
    )
    _logger.info(
        f"Using schema version {schema_version_major.value}.{schema_version_minor.value}"
    )

    if schema_version_major == CodeListConfigJsonSchemaMajorVersion.v1:
        return v1_configdeserialiser.get_deserialiser(
            schema_path, schema_version_minor.value
        )
    else:
        raise ValueError(f"Unhandled major schema version {schema_version_major}")


def _get_schema_code_list_version(
    schema_path: str,
) -> Tuple[CodeListConfigJsonSchemaMajorVersion, CodeListConfigJsonSchemaMinorVersion]:
    if schema_path == V1_CODELIST_SCHEMA_URL:
        schema_path = _LATEST_V1_CODELSIT_SCHEMA_URL

    if schema_path == _v1_0_CODELIST_SCHEMA_URL:
        return (
            CodeListConfigJsonSchemaMajorVersion.v1,
            CodeListConfigJsonSchemaMinorVersion.v0,
        )
    # The second condition in the following makes v1 defaults to the latest minor version of v1.*.
    elif schema_path == _v1_1_CODELIST_SCHEMA_URL:
        return (
            CodeListConfigJsonSchemaMajorVersion.v1,
            CodeListConfigJsonSchemaMinorVersion.v1,
        )
    else:
        raise ValueError(
            f"The $schema '{schema_path}' referenced in the code list config file is not recognised. Please check for any updates to your csvcubed installation."
        )
