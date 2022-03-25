import logging
import os
from pathlib import Path

import pytest
from appdirs import AppDirs
from csvcubed.utils.log import start_logging
from tests.unit import *
from tests.behaviour import *


@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    start_logging(log_dir_name="csvcubed_testing", selected_logging_level=logging.DEBUG)


@pytest.fixture(autouse=True, scope="function")
def clear_log():
    """
    Clears the log file before each test so that searches for log messages are faster, without using slices.
    """
    dirs = AppDirs("csvcubed_testing", "csvcubed")
    log_file_path = Path(dirs.user_log_dir) / "out.log"
    with open(log_file_path, 'w') as f:
        f.write("")
    yield
    pass
