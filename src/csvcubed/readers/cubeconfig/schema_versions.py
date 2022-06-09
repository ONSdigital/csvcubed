"""
Schema Versions
---------------

Contains an enum listing the qube-config.json schema versions recognised by csvcubed.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Optional, Callable, Tuple, List

from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from csvcubed.models.cube import QbCube
from csvcubed.models.validationerror import ValidationError
from csvcubed.readers.cubeconfig.v1 import configdeserialiser as v1_configdeserialiser

_logger = logging.getLogger(__name__)

QubeConfigDeserialiser = Callable[
    [Path, Optional[Path]],
    Tuple[QbCube, List[JsonSchemaValidationError], List[ValidationError]],
]

_v1_0_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.0"
_v1_1_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.1"
_v1_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1"  # v1 defaults to the latest minor version of v1.*.


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


def get_deserialiser_for_schema(
    maybe_schema_path: Optional[str],
) -> QubeConfigDeserialiser:
    """
    Provides a versioned deserialiser function appropriate to the referenced schema.
    """
    # Default to the latest version of the schema.
    schema_path = _v1_1_SCHEMA_URL if maybe_schema_path is None else maybe_schema_path

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
    if schema_path == _v1_0_SCHEMA_URL:
        return (
            QubeConfigJsonSchemaMajorVersion.v1,
            QubeConfigJsonSchemaMinorVersion.v0,
        )
    # The second condition in the following makes v1 defaults to the latest minor version of v1.*.
    elif schema_path == _v1_1_SCHEMA_URL or schema_path == _v1_SCHEMA_URL:
        return (
            QubeConfigJsonSchemaMajorVersion.v1,
            QubeConfigJsonSchemaMinorVersion.v1,
        )
    else:
        raise ValueError(
            f"The $schema '{schema_path}' referenced in the cube config file is not recognised."
        )
