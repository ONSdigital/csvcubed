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
from csvcubed.models.validationerror import ValidationError
from csvcubed.readers.cubeconfig import v1, v1_1

QubeConfigDeserialiser = Callable[
    [Path, Optional[Path]],
    Tuple[QbCube, List[JsonSchemaValidationError], List[ValidationError]],
]

_V1_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.0"
_V1_1_SCHEMA_URL = "/workspaces/csvcubed/csvcubed/csvcubed/schema/cube-config/v1_1/schema.json"  # TODO: Chnage to the purl v1.1 url


class QubeConfigJsonSchemaVersion(Enum):
    """
    Known versions of the QubeConfig JSON Schema and the directory/module name they are contained within.
    """

    V1_0 = "v1_0"
    V1_1 = "v1_1"


def get_deserialiser_for_schema(
    maybe_schema_path: Optional[str],
) -> QubeConfigDeserialiser:
    """
    Provides a versioned deserialiser function appropriate to the referenced schema.
    """
    # Default to the latest version of the schema.
    schema_path = _V1_SCHEMA_URL if maybe_schema_path is None else maybe_schema_path

    schema_version = _get_schema_version(schema_path)
    
    # TODO: Handle schema version detection
    majour_version = 1

    if majour_version == 1:
        return v1.configdeserialiser.get_deserialiser(schema_path, schema_version.value)
    # If there is a new majour version of the cube config schema, another elif needs adding. And a new version of the deseariler needs to be created. For more info, please visit https://purl.org/csv-cubed/schema-versioning
    else:
        raise ValueError(f"Unhandled schema version {schema_version}")


def _get_schema_version(schema_path: str) -> QubeConfigJsonSchemaVersion:
    if schema_path == _V1_SCHEMA_URL:
        return QubeConfigJsonSchemaVersion.V1_0
    elif schema_path == _V1_1_SCHEMA_URL:
        return QubeConfigJsonSchemaVersion.V1_1
    else:
        raise ValueError(
            f"The $schema '{schema_path}' referenced in the cube config file is not recognised."
        )
