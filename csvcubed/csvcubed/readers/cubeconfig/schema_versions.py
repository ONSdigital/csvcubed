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
from csvcubed.readers.cubeconfig import v1

_logger = logging.getLogger(__name__)

QubeConfigDeserialiser = Callable[
    [Path, Optional[Path]],
    Tuple[QbCube, List[JsonSchemaValidationError], List[ValidationError]],
]

_v1_0_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.0"
_v1_1_SCHEMA_URL = "/workspaces/csvcubed/csvcubed/csvcubed/schema/cube-config/v1_1/schema.json"  # TODO: Change to the v1.1 PURL after PR review.


class QubeConfigJsonSchemaMajourVersion(Enum):
    """
    Majour versions of the cube config schema.
    """

    v1 = "v1"


class QubeConfigJsonSchemaMinorVersion(Enum):
    """
    Minor versions of the cube config schema.
    """

    v0 = "0"
    v1 = "1"


def get_deserialiser_for_schema(
    maybe_schema_path: Optional[str],
) -> QubeConfigDeserialiser:
    """
    Provides a versioned deserialiser function appropriate to the referenced schema.
    """
    # Default to the latest version of the schema.
    schema_path = _v1_1_SCHEMA_URL if maybe_schema_path is None else maybe_schema_path

    schema_version_majour, schema_version_minor = _get_schema_version(schema_path)
    _logger.info(f"Using schema version {schema_version_majour}.{schema_version_minor}")

    if schema_version_majour == QubeConfigJsonSchemaMajourVersion.v1:
        return v1.configdeserialiser.get_deserialiser(schema_path)
    else:
        raise ValueError(f"Unhandled schema version {schema_version_majour}")


def _get_schema_version(
    schema_path: str,
) -> Tuple[QubeConfigJsonSchemaMajourVersion, QubeConfigJsonSchemaMinorVersion]:
    if schema_path == _v1_0_SCHEMA_URL:
        return (
            QubeConfigJsonSchemaMajourVersion.v1,
            QubeConfigJsonSchemaMinorVersion.v0,
        )
    elif schema_path == _v1_1_SCHEMA_URL:
        return (
            QubeConfigJsonSchemaMajourVersion.v1,
            QubeConfigJsonSchemaMinorVersion.v1,
        )
    else:
        raise ValueError(
            f"The $schema '{schema_path}' referenced in the cube config file is not recognised."
        )
