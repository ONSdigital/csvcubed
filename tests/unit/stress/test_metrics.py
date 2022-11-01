from datetime import timedelta
import os
from distutils.command.build import build
from genericpath import exists
from importlib.machinery import BuiltinImporter
from tempfile import TemporaryDirectory
from pathlib import Path
from shutil import copy, rmtree

import pytest
from tests.unit.test_baseunit import get_test_cases_dir
from tests.stress.metrics_converter import get_metrics

_stress_test_cases_dir = get_test_cases_dir() / "stress"


def test_stress_metrics():
    """ """
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        copy(
            _stress_test_cases_dir / "buildmetrics.csv",
            tmp_dir,
        )
        copy(
            _stress_test_cases_dir / "jmeter.log",
            tmp_dir,
        )

        build_metrics = get_metrics(
            csv_metrics_in=tmp_dir / "buildmetrics.csv",
            run_type="build",
            run_identifier="someidentifier",
            metrics_out_folder=tmp_dir / "metrics",
        )

        # Cut off precision of time value over seconds (currently returns the time in GMT).
        assert build_metrics.start_time[:8] == "08:04:18"
        assert build_metrics.end_time[:8] == "08:04:22"

        # Round time value to 2 decimal places
        assert round(build_metrics.average_time, 2) == 0.8

        assert build_metrics.total_test_time.seconds == 4

        # Round metrics values to closest number of d.p we could calulate from data
        assert round(build_metrics.max_value_cpu, 2) == 24.67
        assert round(build_metrics.max_value_memory, 2) == 42.61
        assert round(build_metrics.average_value_cpu, 4) == 12.2024
        assert round(build_metrics.average_value_memory, 4) == 42.5142


def test_empty_metrics():
    """ """
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        copy(_stress_test_cases_dir / "buildmetrics_empty.csv", tmp_dir)

        assert pytest.raises(
            IndexError,
            get_metrics,
            tmp_dir / "buildmetrics_empty.csv",
            "build",
            "Some Identifier",
        )


def test_resultant_path():
    """ """
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        copy(
            _stress_test_cases_dir / "buildmetrics.csv",
            tmp_dir,
        )
        copy(
            _stress_test_cases_dir / "jmeter.log",
            tmp_dir,
        )

        run_identifier = "Some Identifier"
        build_metrics = get_metrics(
            tmp_dir / "buildmetrics.csv",
            "build",
            run_identifier,
            metrics_out_folder=tmp_dir / "metrics",
        )

        start_time = "08:04:18"
        assert (tmp_dir / "metrics").exists()
        assert (tmp_dir / "metrics" / run_identifier).exists()
        assert (
            tmp_dir
            / "metrics"
            / run_identifier
            / f"buildmetrics-2022-10-18 {start_time}.csv"
        ).exists()
        assert not (tmp_dir / "jmeter.log").exists()
        assert (tmp_dir / "metrics" / run_identifier / "jmeter.log").exists()


if __name__ == "__main__":
    pytest.main()
