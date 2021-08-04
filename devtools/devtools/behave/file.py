"""
File Steps
----------

"""
from behave import then, Given
from pathlib import Path
import shutil

from .temporarydirectory import get_context_temp_dir_path


@Given('the existing test-case files "{file}"')
def step_impl(context, file):
    test_cases_dir = _get_test_cases_dir()

    matching_files = list(test_cases_dir.rglob(f"**/{file}"))
    if len(matching_files) == 0:
        raise Exception(f"Could not find test-case file {file}")

    temp_dir = get_context_temp_dir_path(context)
    for file in matching_files:
        shutil.copy(file, temp_dir / file.name)


@then('the file at "{file}" should not exist')
def step_impl(context, file):
    temp_dir = get_context_temp_dir_path(context)
    assert not (temp_dir / file).exists()


@then('the file at "{file}" should exist')
def step_impl(context, file):
    temp_dir = get_context_temp_dir_path(context)
    assert (temp_dir / file).exists()


def _get_test_cases_dir(start_dir: Path = Path(".")):
    """First searches for child directories called "test-cases" and then searches recursively up the file system."""
    if str(start_dir) == "/":
        raise Exception(f"Could not find test-cases directory")

    child_test_cases_dirs = list(start_dir.rglob("test-cases"))
    if len(child_test_cases_dirs) == 1:
        return child_test_cases_dirs[0]
    elif len(child_test_cases_dirs) > 1:
        raise Exception(
            f"Found multiple child test-case directories: {', '.join([str(d) for d in child_test_cases_dirs])}"
        )

    return _get_test_cases_dir(start_dir.parent)
