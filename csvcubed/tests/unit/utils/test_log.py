import pytest
#import logging
from csvcubed.utils.log import start_logging


from tests.unit.test_baseunit import get_test_cases_dir

def test_start_logging_accepts_logging_level_inputs():
    logginglvl: str = "err"
    assert(start_logging(logginglvl))

if __name__ == "__main__":
    pytest.main()