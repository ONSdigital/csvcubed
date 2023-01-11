"""
Schema Versions
---------------

Contains an enum listing the qube-config.json schema versions recognised by csvcubed.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from csvcubed.models.cube.cube import QbCube
from csvcubed.models.jsonvalidationerrors import JsonSchemaValidationError
from csvcubed.models.validationerror import ValidationError
from csvcubed.readers.cubeconfig.v1 import configdeserialiser as v1_configdeserialiser

_logger = logging.getLogger(__name__)

QubeConfigDeserialiser = Callable[
    [Path, Optional[Path]],
    Tuple[QbCube, List[JsonSchemaValidationError], List[ValidationError]],
]

""" 
In order to update the MINOR version of qube config, please follow the below steps.
    Step 1: Define a new constant to hold the PURL of the new schema (e.g. _v1_3_SCHEMA_URL).
    Step 2: Update the _LATEST_V1_SCHEMA_URL and _LATEST_SCHEMA_URL so that they are assigned to the constant defined in Step 1.
    Step 3: Add a new enum to the QubeConfigJsonSchemaMinorVersion to represent the new version.
    Step 4: Add a new elif to the _get_schema_version() to represent the new version.
    Step 5: Add the new URL and file path to _hard_coded_map_url_to_file_path in /utils/cache.py and update the value of the default path (denoted with a comment in the map).
    Step 6: Add a new behaviour test to cube.feature file for validating the cube generation using new version of the schema (e.g. "Successfully outputs a cube using schema v1.3" behave scenario).
"""

_v1_0_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.0"
_v1_1_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.1"
_v1_2_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.2"
_v1_3_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.3"
_v1_4_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.4"
V1_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1"  # v1 defaults to the latest minor version of v1.*.

_LATEST_V1_SCHEMA_URL = _v1_4_SCHEMA_URL
"""
    This holds the URL identifying the latest minor version of the V1 schema.

    When adding a new minor version to the V1 schema, you must update this variable.
"""

_LATEST_SCHEMA_URL = _v1_4_SCHEMA_URL
"""
    This holds the URL identifying the latest version of the schema.

    When adding a new schema version, you must update this variable.
"""


class QubeConfigJsonSchemaMajorVersion(Enum):
    """
    Major versions of the cube config schema.
    """

    v1 = 1


class QubeConfigJsonSchemaMinorVersion(Enum):
    """
    Minor versions of the cube config schema.
    """

    v0 = 0
    v1 = 1
    v2 = 2
    v3 = 3
    v4 = 4


def get_deserialiser_for_schema(
    maybe_schema_path: Optional[str],
) -> QubeConfigDeserialiser:
    """
    Provides a versioned deserialiser function appropriate to the referenced schema.
    """
    # Default to the latest version of the schema.
    schema_path = _LATEST_SCHEMA_URL if maybe_schema_path is None else maybe_schema_path

    schema_version_major, schema_version_minor = _get_schema_version(schema_path)
    _logger.info(
        f"Using schema version {schema_version_major.value}.{schema_version_minor.value}"
    )

    if schema_version_major == QubeConfigJsonSchemaMajorVersion.v1:
        return v1_configdeserialiser.get_deserialiser(
            schema_path, schema_version_minor.value
        )
    else:
        raise ValueError(f"Unhandled major schema version {schema_version_major}")


def _get_schema_version(
    schema_path: str,
) -> Tuple[QubeConfigJsonSchemaMajorVersion, QubeConfigJsonSchemaMinorVersion]:
    if schema_path == V1_SCHEMA_URL:
        schema_path = _LATEST_V1_SCHEMA_URL

    if schema_path == _v1_0_SCHEMA_URL:
        return (
            QubeConfigJsonSchemaMajorVersion.v1,
            QubeConfigJsonSchemaMinorVersion.v0,
        )
    # The second condition in the following makes v1 defaults to the latest minor version of v1.*.
    elif schema_path == _v1_1_SCHEMA_URL:
        return (
            QubeConfigJsonSchemaMajorVersion.v1,
            QubeConfigJsonSchemaMinorVersion.v1,
        )
    elif schema_path == _v1_2_SCHEMA_URL:
        return (
            QubeConfigJsonSchemaMajorVersion.v1,
            QubeConfigJsonSchemaMinorVersion.v2,
        )
    elif schema_path == _v1_3_SCHEMA_URL:
        return (
            QubeConfigJsonSchemaMajorVersion.v1,
            QubeConfigJsonSchemaMinorVersion.v3,
        )
    elif schema_path == _v1_4_SCHEMA_URL:
        return (
            QubeConfigJsonSchemaMajorVersion.v1,
            QubeConfigJsonSchemaMinorVersion.v4,
        )
    else:
        raise ValueError(
            f"The $schema '{schema_path}' referenced in the cube config file is not recognised. Please check for any updates to your csvcubed installation."
        )
