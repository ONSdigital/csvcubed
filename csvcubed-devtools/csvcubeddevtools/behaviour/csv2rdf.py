"""
csv2rdf
-------

behave functionality to run csv2rdf on some output
"""
from behave import step
from pathlib import Path
import docker
import sys
from typing import Tuple, Optional
from tempfile import TemporaryDirectory


from csvcubeddevtools.helpers.tar import dir_to_tar, extract_tar
from csvcubeddevtools.behaviour.temporarydirectory import get_context_temp_dir_path

client = docker.from_env()
client.images.pull("gsscogs/csv2rdf")


def _run_csv2rdf(context, metadata_file_path: Path) -> Tuple[int, str, Optional[str]]:
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        csv2rdf = client.containers.create(
            "gsscogs/csv2rdf",
            command=f"csv2rdf -u /tmp/{metadata_file_path.name} -o /tmp/csv2rdf.ttl -m annotated",
        )
        csv2rdf.put_archive("/tmp", dir_to_tar(metadata_file_path.parent))

        csv2rdf.start()
        response: dict = csv2rdf.wait()
        exit_code = response["StatusCode"]
        sys.stdout.write(csv2rdf.logs().decode("utf-8"))

        output_stream, output_stat = csv2rdf.get_archive("/tmp/csv2rdf.ttl")
        extract_tar(output_stream, tmp_dir)
        maybe_output_file = tmp_dir / "csv2rdf.ttl"
        if maybe_output_file.exists():
            with open(maybe_output_file, "r") as f:
                ttl_out = f.read()
        else:
            ttl_out = ""

    return exit_code, csv2rdf.logs().decode("utf-8"), ttl_out


@step('csv2rdf on "{file}" should succeed')
def step_impl(context, file: str):
    """csv2rdf on "{file}" should succeed"""
    temp_dir = get_context_temp_dir_path(context)
    exit_code, logs, ttl_out = _run_csv2rdf(context, temp_dir / file)
    assert exit_code == 0

    context.turtle = ttl_out


@step("csv2rdf on all CSV-Ws should succeed")
def step_impl(context):
    """csv2rdf on all CSV-Ws should succeed"""
    temp_dir = get_context_temp_dir_path(context)
    csvw_metadata_files = temp_dir.rglob("*.csv-metadata.json")
    context.turtle = ""

    for file in csvw_metadata_files:
        exit_code, logs, ttl_out = _run_csv2rdf(context, temp_dir / file)
        assert exit_code == 0

        context.turtle += ttl_out


@step('csv2rdf on "{file}" should fail with "{expected}"')
def step_impl(context, file: str, expected: str):
    """csv2rdf on \"{file}\" should fail with \"{expected}\" """
    temp_dir = get_context_temp_dir_path(context)
    exit_code, logs, ttl_out = _run_csv2rdf(context, temp_dir / file)
    assert exit_code == 1
    assert expected in logs

    context.turtle = ttl_out
