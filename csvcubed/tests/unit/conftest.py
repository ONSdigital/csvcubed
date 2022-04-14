import logging
import shutil
from pathlib import Path

import appdirs
import pytest

from csvcubed.utils.log import start_logging

_user_log_dir = Path(appdirs.AppDirs("csvcubed_testing", "csvcubed").user_log_dir)


@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    """Make sure to remove all the existing log files so we don't contaminate the tests."""
    shutil.rmtree(_user_log_dir)

    root_logger = logging.getLogger("csvcubed")
    for filter in root_logger.filters:
        root_logger.removeFilter(filter)
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    start_logging(log_dir_name="csvcubed_testing", selected_logging_level=logging.DEBUG)
