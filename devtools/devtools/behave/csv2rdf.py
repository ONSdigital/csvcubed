"""
behave functionality to run csv-lint on some output
"""
from behave import *
from nose.tools import *
from pathlib import Path
import docker
import sys
from typing import Tuple, Optional
from tempfile import TemporaryDirectory


def _run_csv2rdf(metadata_file_path: Path) -> Tuple[int, str, Optional[str]]:
    with TemporaryDirectory() as tmp_dir:
        client = docker.from_env()
        csv2rdf = client.containers.create(
            'gsscogs/csv2rdf',
            command=f'csv2rdf -u /workspace/{metadata_file_path.name} -o /output/csv2rdf.ttl',
            volumes={
                str(metadata_file_path.parent.absolute()): {
                    "bind": "/workspace",
                    "mode": "ro"
                },
                tmp_dir: {
                    "bind": "/output",
                    "mode": "rw"
                }
            }
        )
        csv2rdf.start()
        response: dict = csv2rdf.wait()
        exit_code = response["StatusCode"]
        sys.stdout.write(csv2rdf.logs().decode('utf-8'))

        tmp_dir_path = Path(str(tmp_dir))
        maybe_output_file = tmp_dir_path / "csv2rdf.ttl"
        if maybe_output_file.exists():
            with open(maybe_output_file, "r") as f:
                ttl_out = f.read()
        else:
            ttl_out = ""

    return exit_code, csv2rdf.logs().decode('utf-8'), ttl_out


@step("csv2rdf on \"{file}\" should succeed")
def step_impl(context, file: str):
    exit_code, logs, ttl_out = _run_csv2rdf(Path(file))
    assert_equal(exit_code, 0)

    context.turtle = ttl_out


@step('csv2rdf on \"{file}\" should fail with "{expected}"')
def step_impl(context, file: str, expected: str):
    exit_code, logs, ttl_out = _run_csv2rdf(Path(file))
    assert_equal(exit_code, 1)
    assert expected in logs

    context.turtle = ttl_out
