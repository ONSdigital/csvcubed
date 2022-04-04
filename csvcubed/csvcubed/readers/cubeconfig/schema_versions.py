"""
Schema Versions
---------------

Contains an enum listing the qube-config.json schema versions recognised by csvcubed.
"""
from enum import Enum
from pathlib import Path
from typing import Optional, Callable, Tuple, List

from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from csvcubed.models.cube import QbCube
from csvcubed.readers.cubeconfig import v1_0

QubeConfigDeserialiser = Callable[
    [Path, Optional[Path]], Tuple[QbCube, List[JsonSchemaValidationError]]
]

_V1_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.0"


class QubeConfigJsonSchemaVersion(Enum):
    """
    Known versions of the QubeConfig JSON Schema and the directory/module name they are contained within.
    """

    V1_0 = "v1_0"


def get_deserialiser_for_schema(
    maybe_schema_path: Optional[str],
) -> QubeConfigDeserialiser:
    """
    Provides a versioned deserialiser function appropriate to the referenced schema.
    """
    # Default to the latest version of the schema.
    schema_path = _V1_SCHEMA_URL if maybe_schema_path is None else maybe_schema_path

    schema_version = _get_schema_version(schema_path)

    if schema_version == QubeConfigJsonSchemaVersion.V1_0:
        return v1_0.configdeserialiser.get_deserialiser(
            schema_path, schema_version.value
        )
    else:
        raise ValueError(f"Unhandled schema version {schema_version}")


def _get_schema_version(schema_path: str) -> QubeConfigJsonSchemaVersion:
    if schema_path == _V1_SCHEMA_URL:
        return QubeConfigJsonSchemaVersion.V1_0
    else:
        raise ValueError(
            f"The $schema '{schema_path}' referenced in the cube config file is not recognised."
        )
