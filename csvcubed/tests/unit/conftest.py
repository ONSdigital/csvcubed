import logging

import pytest

from csvcubed.utils.log import start_logging
from tests.unit import *
from tests.behaviour import *


@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    start_logging(console_level=logging.DEBUG)
