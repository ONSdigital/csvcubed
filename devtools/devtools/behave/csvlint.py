"""
behave functionality to run csv-lint on some output
"""
from behave import *
from nose.tools import *
from pathlib import Path
import docker
import sys
from typing import Tuple


def _run_csvlint(metadata_file_path: Path) -> Tuple[int, str]:
    client = docker.from_env()
    csvlint = client.containers.create(
        'gsscogs/csvlint',
        command=f'csvlint -s /workspace/{metadata_file_path.name}',
        volumes={
            "/workspace": {
                "bind": str(metadata_file_path.parent.absolute()),
                "mode": "ro"
            }
        }
    )
    csvlint.start()
    response: dict = csvlint.wait()
    exit_code = response["StatusCode"]
    sys.stdout.write(csvlint.logs().decode('utf-8'))
    return exit_code, csvlint.logs().decode('utf-8')


@step("csvlint validates ok")
def step_impl(context):
    exit_code, logs = _run_csvlint(context)
    assert_equal(exit_code, 0)


@step('csvlint should fail with "{expected}"')
def step_impl(context, expected):
    exit_code, logs = _run_csvlint(context)
    assert_equal(exit_code, 1)
    assert expected in logs
