from tempfile import TemporaryDirectory
from pathlib import Path

import pytest
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir()



def test_stress_metrics():
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)


if __name__ == "__main__":
    pytest.main()