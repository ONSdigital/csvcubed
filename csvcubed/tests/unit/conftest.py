import pytest

from csvcubed.utils.log import start_logging
from tests.unit import *
from tests.behaviour import *


@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    start_logging(
        logdir = 'log_test_dir', 
        selected_logging_level = 'err'
    )

