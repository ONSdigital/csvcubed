from os import getcwd
from pathlib import Path

from csvcubed.cli.build_code_list import build_code_list
from new_command import write_the_file
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir()


def test_does_it_work():
    """Function to test the basic funtionalities"""
    path_to_out = Path(getcwd() + "/out")

    write_the_file(path_to_out)


def test_new_command():
    """ """

    path_to_json = (
        _test_case_base_dir
        / "readers"
        / "code-list-config"
        / "v1.0"
        / "code_list_config_none_hierarchical.json"
    )

    build_code_list(path_to_json, Path(getcwd() + "/out"))
