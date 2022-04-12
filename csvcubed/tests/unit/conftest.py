import logging

import pytest

from csvcubed.utils.log import start_logging


@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    start_logging(log_dir_name="csvcubed_testing", selected_logging_level=logging.DEBUG)
