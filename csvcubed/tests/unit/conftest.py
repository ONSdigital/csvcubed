import logging

import pytest

from csvcubed.utils.log import start_logging
from tests.unit import *
from tests.behaviour import *


@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    start_logging(selected_logging_level = 'err')
    start_logging(selected_logging_level = '')
    start_logging(selected_logging_level = 'hello')
    start_logging(selected_logging_level = None)
    start_logging(selected_logging_level = 3)
    logginglvl:int = 5
    start_logging(selected_logging_level = logginglvl)

