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


class QubeConfigJsonSchemaVersion:
    """
    Holds the recognised schema URLs (and hence versions) of the qube-config.json syntax.
    """

    DEFAULT_V1_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.0"

    @staticmethod
    def get_deserialiser_for_schema(
        schema: Optional[str],
    ) -> QubeConfigDeserialiser:
        if schema is None:
            return v1_0.configdeserialiser.get_cube_from_config_json
        elif schema == QubeConfigJsonSchemaVersion.DEFAULT_V1_SCHEMA_URL:
            return v1_0.configdeserialiser.get_cube_from_config_json
        else:
            raise ValueError(
                f"The $schema '{schema}' referenced in the cube config file is not recognised."
            )
