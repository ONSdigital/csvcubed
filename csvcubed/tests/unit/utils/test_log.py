import logging
from csvcubed.utils.log import start_logging
import pytest

from tests.unit.test_baseunit import get_test_cases_dir

def start_logging_works():
    logginglvl: int = logging.WARNING
    assert(start_logging(logginglvl))