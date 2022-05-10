"""
Schema Versions
---------------

Contains an enum listing the qube-config.json schema versions recognised by csvcubed.
"""
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Callable, Tuple, List

from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from csvcubed.models.cube import QbCube
from csvcubed.models.validationerror import ValidationError
from csvcubed.readers.cubeconfig import v1, v1_1

QubeConfigDeserialiser = Callable[
    [Path, Optional[Path]],
    Tuple[QbCube, List[JsonSchemaValidationError], List[ValidationError]],
]

_v1_0_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.0"
_v1_1_SCHEMA_URL = "/workspaces/csvcubed/csvcubed/csvcubed/schema/cube-config/v1_1/schema.json"  # TODO: Chnage to the purl v1.1 url


class QubeConfigJsonSchemaMinorVersion(Enum):
    """
    Minor versions of the cube config schema.
    """

    v0 = "0"
    v1 = "1"


class QubeConfigJsonSchemaMajourVersion(Enum):
    """
    Majour versions of the cube config schema.
    """

    v1 = "v1"


def get_deserialiser_for_schema(
    maybe_schema_path: Optional[str],
) -> QubeConfigDeserialiser:
    """
    Provides a versioned deserialiser function appropriate to the referenced schema.
    """
    # Default to the latest version of the schema.
    schema_path = _v1_1_SCHEMA_URL if maybe_schema_path is None else maybe_schema_path

    schema_version_majour, _ = _get_schema_version(schema_path)
    if schema_version_majour == QubeConfigJsonSchemaMajourVersion.v1:
        return v1.configdeserialiser.get_deserialiser(
            schema_path, schema_version_majour.value
        )
    # If there is a new majour version of the cube config schema, another elif needs adding here. And a new version of the deseariler needs to be created. For more info, please visit https://purl.org/csv-cubed/schema-versioning
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
