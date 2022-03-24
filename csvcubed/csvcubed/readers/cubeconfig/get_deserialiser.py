import logging
from pathlib import Path
from typing import Optional, Tuple, List, Callable

from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from csvcubed.models.cube import QbCube
from csvcubed.readers.cubeconfig import v1_0
from csvcubed.readers.cubeconfig.schema_versions import QubeConfigJsonSchemaVersion
from csvcubed.readers.cubeconfig.utils import load_resource

_logger = logging.getLogger(__name__)


def get_deserialiser_for_schema(
    json_config_path: Optional[Path],
) -> Callable[[Path, Optional[Path]], Tuple[QbCube, List[JsonSchemaValidationError]]]:
    """
    Return the correct version of the config deserialiser based on the schema in the cube config file
    """
    if json_config_path:
        config = load_resource(json_config_path)
        schema = config.get(
            "$schema", QubeConfigJsonSchemaVersion.DEFAULT_V1_SCHEMA_URL.value
        )

        if schema == QubeConfigJsonSchemaVersion.DEFAULT_V1_SCHEMA_URL.value:
            return v1_0.configdeserialiser.get_cube_from_config_json
        else:
            raise ValueError(
                f"The $schema '{schema}' referenced in the cube config file is not recognised."
            )

    else:
        return v1_0.configdeserialiser.get_cube_from_config_json
