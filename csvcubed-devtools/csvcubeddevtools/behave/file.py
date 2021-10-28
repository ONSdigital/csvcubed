"""
File Steps
----------

"""
from behave import then, Given
from pathlib import Path
import shutil

from .temporarydirectory import get_context_temp_dir_path


@Given('the existing test-case file "{file}"')
def step_impl(context, file):
    test_cases_dir = _get_test_cases_dir()
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
    test_cases_dir = _get_test_cases_dir()

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


@then('the file at "{file}" should exist')
def step_impl(context, file):
    temp_dir = get_context_temp_dir_path(context)
    assert (temp_dir / file).exists(), file


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

    return _get_test_cases_dir(start_dir.absolute().parent)
