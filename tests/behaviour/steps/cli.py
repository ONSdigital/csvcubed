import json
import shutil
import subprocess
from pathlib import Path
from typing import Tuple

from appdirs import AppDirs
from behave import then, when
from csvcubeddevtools.behaviour.temporarydirectory import get_context_temp_dir_path


@when('the csvcubed CLI is run with "{arguments}"')
def step_impl(context, arguments: str):
    command: str = f"csvcubed {arguments.strip()}"
    (status_code, response) = run_command_in_temp_dir(context, command)
    context.csvcubed_cli_result = (status_code, response)
    dirs = AppDirs("csvcubed-cli", "csvcubed")
    context.csvcubed_log_location = Path(dirs.user_log_dir)


@then("the csvcubed CLI should succeed")
def step_impl(context):
    (status_code, response) = context.csvcubed_cli_result
    assert status_code == 0, (status_code, response)
    assert "Build Complete" in response, response


@then("the csvcubed CLI should fail with status code {status_code}")
def step_impl(context, status_code: str):
    (status_code, _) = context.csvcubed_cli_result
    assert status_code == int(status_code), status_code


@then('the csvcubed CLI should print "{printed_text}"')
def step_impl(context, printed_text: str):
    (_, response) = context.csvcubed_cli_result
    assert printed_text in response, response


@then('the csvcubed CLI should not print "{printed_text}"')
def step_impl(context, printed_text: str):
    (_, response) = context.csvcubed_cli_result
    assert printed_text not in response, response


@then("the validation-errors.json file should contain")
def step_impl(context):
    tmp_dir_path = get_context_temp_dir_path(context)
    expected_text_contents: str = context.text.strip()
    validation_errors_file = tmp_dir_path / "out" / "validation-errors.json"
    assert validation_errors_file.exists()

    with open(validation_errors_file, "r") as f:
        file_contents = f.read()

    # Ensure JSON is valid.
    json_validation_errors = json.loads(file_contents)
    assert isinstance(json_validation_errors, list), type(json_validation_errors)

    assert expected_text_contents in file_contents, file_contents


@then("the log file should contain")
def step_impl(context):
    log_file = context.csvcubed_log_location
    expected_text_contents: str = context.text.strip()
    assert log_file.exists()

    with open(log_file, "r") as f:
        file_contents = f.read()

    assert expected_text_contents in file_contents, file_contents


@then("the log file should exist")
def step_impl(context):
    log_dir = Path(context.csvcubed_log_location)
    assert log_dir.exists(), str(log_dir)
    log_file = log_dir / "out.log"
    assert log_file.exists(), f"Files in log directory: {list(log_dir.rglob('**/*'))}"


@then("the command line output should display the log message")
def step_impl(context):
    (status_code, log_message) = context.csvcubed_cli_result
    expected_log_message = context.text.strip()
    assert expected_log_message in log_message, log_message


@then("the command line output should not display the log message")
def step_impl(context):
    (status_code, log_message) = context.csvcubed_cli_result
    expected_log_message = context.text.strip()
    assert expected_log_message not in log_message, log_message


@then("remove test log files")
def step_impl(context):
    shutil.rmtree(context.csvcubed_log_location)


def run_command_in_temp_dir(context, command: str) -> Tuple[int, str]:
    tmp_dir_path = get_context_temp_dir_path(context)

    # Use temp files not a PIPE, a PIPE has a tiny buffer than
    # can deadlock or result in eroneous resource exhaustion behaviour
    # where encountering some of our larger outputs (jsonSchemaErrors result
    # in large writes to stdout)
    Path(tmp_dir_path / "buffer").mkdir()
    stdout_path = Path(tmp_dir_path / "buffer" / "stdout")
    stderr_path = Path(tmp_dir_path / "buffer" / "stderr")

    with open(stdout_path, "w") as stdout_file, open(stderr_path, "w") as stderr_file:

        process = subprocess.Popen(
            command,
            shell=True,
            cwd=tmp_dir_path.resolve(),
            stdout=stdout_file,
            stderr=stderr_file,
        )

    status_code = process.wait()

    with open(stdout_path) as stdout_file, open(stderr_path) as stderr_file:
        response = stdout_file.read() + stderr_file.read()

    return status_code, response
