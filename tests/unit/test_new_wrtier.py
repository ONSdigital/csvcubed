from os import getcwd
from pathlib import Path

from csvcubed.cli.build_code_list import build_code_list
from new_command import write_the_file


def test_does_it_work():
    """Function to test the basic funtionalities"""
    path_to_out = Path(getcwd() + "/out")

    write_the_file(path_to_out)


def test_new_command():
    """ """
    build_code_list()
