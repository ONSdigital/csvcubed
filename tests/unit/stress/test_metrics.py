from datetime import timedelta
import os
from distutils.command.build import build
from genericpath import exists
from importlib.machinery import BuiltinImporter
from tempfile import TemporaryDirectory
from pathlib import Path
from shutil import copy

import pytest
from tests.unit.test_baseunit import get_test_cases_dir
from tests.stress.metrics_converter import get_metrics

_stress_test_cases_dir = get_test_cases_dir() / "stress"


def test_stress_metrics():
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        copy(_stress_test_cases_dir / "buildmetrics.csv", tmp_dir)
        copy(_stress_test_cases_dir / "inspectmetrics.csv", tmp_dir)

        build_metrics = get_metrics(tmp_dir / "buildmetrics.csv", "build", "Some Identifier")
    
        # Cut off precision of time value over seconds.
        assert build_metrics.start_time[:8] == "09:04:18"
        assert build_metrics.end_time[:8] == "09:04:22"

        # Round time value to 2 decimal places
        assert round(build_metrics.average_time, 2) == 0.8

        assert build_metrics.total_test_time.seconds == 4

        # Round metrics values to closest number of d.p we could calulate from data
        assert round(build_metrics.max_value_cpu, 2) == 24.673
        assert round(build_metrics.max_value_memory, 2) == 42.61
        assert round(build_metrics.average_value_cpu, 4) == 12.2024
        assert round(build_metrics.average_value_memory, 4) == 42.5142

def test_empty_metrics():
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        copy(_stress_test_cases_dir / "buildmetrics_empty.csv", tmp_dir)
        copy(_stress_test_cases_dir / "inspectmetrics.csv", tmp_dir)

        build_metrics = get_metrics(tmp_dir / "buildmetrics_empty.csv", "build", "Some Identifier")
    
        #assert am error is shown which states that no values have been recorded by the listener 

def test_resultant_path():
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        copy(_stress_test_cases_dir / "buildmetrics.csv", tmp_dir)
        copy(_stress_test_cases_dir / "inspectmetrics.csv", tmp_dir)

        build_metrics = get_metrics(tmp_dir / "buildmetrics.csv", "build", "Some Identifier")
    
        start_time = "09:04:18"
        assert os.path.exists(Path("metrics/"))
        assert os.path.exists(Path("metrics/Some Identifier/"))
        assert os.path.isfile(Path(f"metrics/Some Identifier/Buildmetrics-2022-10-18 {start_time}.csv"))

if __name__ == "__main__":
    pytest.main()