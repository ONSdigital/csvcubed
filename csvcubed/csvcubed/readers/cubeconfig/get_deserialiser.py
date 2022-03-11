import logging
from pathlib import Path
from typing import Optional

import csvcubed.readers.cubeconfig.v1_0.configdeserialiser
from csvcubed.readers.cubeconfig import v1_0
from csvcubed.readers.cubeconfig.utils import load_resource

DEFAULT_V1_SCHEMA_PURL = "https://purl.archive.org/purl/csv-cubed/qube-config/v1.0"
V2_SCHEMA_PURL = "http://purl.org/csv-cubed/qube-schema/v2.0"
DEV_SCHEMA_PATH = "./csvcubed/schema/cube-config-schema.json"

_logger = logging.getLogger(__name__)


def get_deserialiser(config_path: Optional[Path]) -> object:
    """
    Return the correct version of the config deserialiser based on the schema in the cube config file
    """
    if config_path:
        config = load_resource(config_path)
        schema = config.get("$schema", DEFAULT_V1_SCHEMA_PURL)

        if schema == DEFAULT_V1_SCHEMA_PURL:
            return csvcubed.readers.cubeconfig.v1_0.configdeserialiser.get_cube_from_config_json

        elif schema == DEV_SCHEMA_PATH:
            return csvcubed.readers.cubeconfig.v1_0.configdeserialiser.get_cube_from_config_json

        else:
            msg = f"The $schema '{schema}' referenced in the cub config file is not recognised."
            _logger.error(msg)
            raise ValueError(msg)

    else:
        return v1_0.configdeserialiser.get_cube_from_config_json