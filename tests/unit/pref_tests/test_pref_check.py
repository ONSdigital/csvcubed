import importlib
from csvcubeddevtools.helpers.file import get_test_cases_dir
from tests.pref_improvement.pref_check import (
    list_classes_in_file,
    generate_modules,
    check_for_dataclass,
    _map_to_module_name,
    acess_all_folders_return_all_files,
)

from pathlib import Path

def test_map_to_module_name():
    """
    test to ensure it returns the corrects name
    """

    path = get_test_cases_dir() / "test_class_collector" / "test_file.py"

    pyscript = _map_to_module_name(str(path))

    assert pyscript == "test_file"

    path = Path("__init__.py")

    init_file = _map_to_module_name(str(path))

    assert init_file is None


def test_acess_all_folders_return_all_files():

    path_to_file = get_test_cases_dir() / "test_class_collector"

    list_of_files = acess_all_folders_return_all_files(path_to_file)

    assert len(list_of_files) == 3


def test_list_classes_in_file():

    path = get_test_cases_dir() / "test_class_collector" / "test_file.py"
    imported_module = importlib.import_module(
        "tests.test-cases.test_class_collector.test_file"
    )
    second_list = list(list_classes_in_file(imported_module, path))

    assert len(second_list) == 3
    assert set([c.__name__ for c in second_list]) == {
        "Myclass",
        "SecondClass",
        "ThirdClass",
    }


def test_generate_modules():

    path = get_test_cases_dir() / "test_class_collector" / "test_file.py"

    result = generate_modules(
        path, get_test_cases_dir().parent, root_package_name="tests"
    )
    assert str(result.__name__) == "tests.test-cases.test_class_collector.test_file"


def test_check_for_dataclass():

    path = get_test_cases_dir() / "test_class_collector" / "test_file.py"
    imported_module = importlib.import_module(
        "tests.test-cases.test_class_collector.test_file"
    )
    second_list = list_classes_in_file(imported_module, path)

    data_classes = list(check_for_dataclass(second_list))

    assert len(data_classes) == 1
    assert data_classes[0].__name__ == "ThirdClass"
