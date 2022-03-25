import logging

import pytest

from csvcubed.readers.cubeconfig import schema_versions
from csvcubed.utils.log import start_logging
from definitions import ROOT_DIR_PATH


@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    start_logging(log_dir_name="csvcubed_testing", selected_logging_level=logging.DEBUG)


@pytest.fixture(autouse=True, scope="session")
def set_testing_v1_schema_url():
    """
    Configure the tests to believe that the `https://purl.org/csv-cubed/qube-config/v1.0` is secretly replaced with
    the local (and hence latest) copy of the schema.
    """
    schema_versions._schema_url_overrides = {
        "https://purl.org/csv-cubed/qube-config/v1.0": str(
            ROOT_DIR_PATH / "csvcubed" / "schema" / "cube-config-schema.json"
        )
    }
