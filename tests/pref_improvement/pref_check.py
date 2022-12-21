"""
The inspect module helps to  get information about live objects such as modules, classes, methods, 
functions, tracebacks, frame objects, and code objects.
"""
import inspect

import importlib
import sys
from typing import Iterable
from dataclasses import is_dataclass, fields
from pathlib import Path

import csvcubed
from csvcubed.definitions import APP_ROOT_DIR_PATH
from csvcubed.models.validatedmodel import ValidatedModel


def list_classes_in_file(imported_module, file_name: Path) -> Iterable[type]:
    """scan throught each file and check if the members are classes"""

    for (name, value) in inspect.getmembers(imported_module):
        if inspect.isclass(value):
            defined_in = inspect.getfile(value)
            # check if the class is localy defined (checks if the definition adress anad the file adress matches)
            if defined_in == str(file_name.absolute()):
                yield value


def check_for_dataclass(classes: Iterable[type]) -> Iterable[type]:
    """checks for the class it a dataclass"""
    for clazz in classes:
        if is_dataclass(clazz):
            yield clazz


def acess_all_folders_return_all_files(path_name: Path) -> list[str]:
    """acessing all files from the path directory that ends with .py"""
    return list(path_name.glob("**/*.py"))


def _map_to_module_name(path_part: str) -> str:
    """check for the path conains an init file or is it a python sript (ends with a .py) and returns the module name"""
    if path_part == "__init__.py":
        return None
    elif path_part.endswith(".py"):
        return inspect.getmodulename(path_part)
    else:
        return path_part


def generate_modules(
    path_to_file: Path, path_to_root_dir: Path, root_package_name: str = "csvcubed"
):

    path_parts = [
        _map_to_module_name(p) for p in path_to_file.relative_to(path_to_root_dir).parts
    ]
    path_parts = [root_package_name] + [p for p in path_parts if p is not None]
    module_name = ".".join(path_parts)

    # check if the module(file) has already ben loaded
    if module_name in sys.modules:
        imported_module = sys.modules[module_name]
    else:
        # if not then get the module name from the path then load it into memory
        module_spec = importlib.util.spec_from_file_location(module_name, path_to_file)
        imported_module = importlib.import_module(module_name)

    return imported_module


def _get_all_classes(path_to_folder: Path) -> Iterable[type]:
    # getting all the python script paths
    list_of_all_files = acess_all_folders_return_all_files(path_to_folder)

    for x in list_of_all_files:
        imported_module = generate_modules(x, path_to_folder)
        # loops trough each file and returns every class from the files
        for clazz in list_classes_in_file(imported_module, x):
            yield clazz


def main():
    # listing all the classes from each file in the directory and subdirectory given.
    all_classes = _get_all_classes(APP_ROOT_DIR_PATH)

    # list all dataclasses(the classes that have the datacall decorator)
    all_data_classes = check_for_dataclass(all_classes)
    failed = False
    validated_model_classes = []
    for clazz in all_data_classes:
        if issubclass(clazz, ValidatedModel) and not inspect.isabstract(clazz):
            validated_model_classes.append(clazz)

    for validated_model_class in validated_model_classes:
        validated_model = validated_model_class.__new__(validated_model_class)
        field_names_validated = set(validated_model._get_validations().keys())
        field_names = {f.name for f in fields(validated_model)}

        if field_names_validated != field_names:

            failed = True
            not_validated = field_names - field_names_validated
            print(
                f"In {validated_model_class.__name__} ({inspect.getfile(validated_model_class)}) you have not validated {', '.join(not_validated)}"
            )
            print(format(field_names))  # This returns empty

    if failed:
        exit(1)


if __name__ == "__main__":
    main()
