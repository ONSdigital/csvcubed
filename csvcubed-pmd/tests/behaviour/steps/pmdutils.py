from behave import when, then
from typing import Tuple
from csvcubeddevtools.behaviour.temporarydirectory import get_context_temp_dir_path
import subprocess


@when('the pmdutils command CLI is run with "{arguments}"')
def step_impl(context, arguments: str) -> None:
    command: str = f"pmdutils {arguments.strip()}"
    (status_code, response) = run_command_in_temp_dir(context, command)
    context.cli_result = (status_code, response)


@then("the CLI should succeed")
def step_impl(context):
    (status_code, response) = context.cli_result
    assert status_code == 0, (status_code, response)


@then("the CLI should fail with status code {expected_status_code}")
def step_impl(context, expected_status_code: str):
    (status_code, response) = context.cli_result
    assert status_code == int(expected_status_code), status_code


@then('the CLI should print "{printed_text}"')
def step_impl(context, printed_text: str):
    (status_code, response) = context.cli_result
    assert printed_text in response, response


def run_command_in_temp_dir(context, command: str) -> Tuple[int, str]:
    tmp_dir_path = get_context_temp_dir_path(context)
    process = subprocess.Popen(
        command,
        shell=True,
        cwd=tmp_dir_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    status_code = process.wait()
    response = process.stdout.read().decode("utf-8") + process.stderr.read().decode(
        "utf-8"
    )
    return status_code, response
