"""
File Steps
----------

"""
from behave import then, Given
from pathlib import Path
import shutil
from difflib import Differ
from textwrap import dedent

from .temporarydirectory import get_context_temp_dir_path
from csvcubeddevtools.helpers.file import get_test_cases_dir


@Given('the existing test-case file "{file}"')
def step_impl(context, file):
    test_cases_dir = get_test_cases_dir()
    test_case_file = test_cases_dir / file

    if not test_case_file.exists():
        raise Exception(f"Could not find test-case file {file}")

    temp_dir = get_context_temp_dir_path(context)
    output_file_path = temp_dir.joinpath(test_case_file.relative_to(test_cases_dir))

    _ensure_directory_hierarchy_exists(output_file_path.parent)

    shutil.copy(test_case_file, output_file_path)


def _ensure_directory_hierarchy_exists(directory: Path):
    if not directory.exists():
        _ensure_directory_hierarchy_exists(directory.parent)
        directory.mkdir()


@Given('the existing test-case files "{files_glob}"')
def step_impl(context, files_glob: str):
    test_cases_dir = get_test_cases_dir()

    matching_files = list(test_cases_dir.rglob(f"**/{files_glob}"))
    if len(matching_files) == 0:
        raise Exception(f"Could not find test-case file(s) {files_glob}")

    temp_dir = get_context_temp_dir_path(context)
    for file in matching_files:
        shutil.copy(file, temp_dir / file.name)


@then('the file at "{file}" should not exist')
def step_impl(context, file):
    temp_dir = get_context_temp_dir_path(context)
    assert not (temp_dir / file).exists()


@then('the file at "{file}" should contain')
def step_impl(context, file):
    temp_dir = get_context_temp_dir_path(context)
    with open(temp_dir / file, "r") as f:
        file_contents = f.read().strip().splitlines(keepends=True)
    expected_contents = dedent(context.text).splitlines(keepends=True)
    differ = Differ()
    comparison_result = list(differ.compare(expected_contents, file_contents))
    assert len(comparison_result) == len(expected_contents), "".join(comparison_result)


@then('the file at "{file}" should exist')
def step_impl(context, file):
    temp_dir = get_context_temp_dir_path(context)
    assert (temp_dir / file).exists(), file
