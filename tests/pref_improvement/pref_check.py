import inspect
import importlib
import sys
from typing import Iterable
from dataclasses import is_dataclass, fields
from pathlib import Path

import csvcubed
from csvcubed.definitions import APP_ROOT_DIR_PATH
from csvcubed.models.validatedmodel import ValidatedModel

# scan throught each file and check if the members are classes
def list_classes_in_file(imported_module, file_name: Path) -> Iterable[type]:

    for (name, value) in inspect.getmembers(imported_module):
        if inspect.isclass(value):
            defined_in = inspect.getfile(value)
            # check if the class is localy defined (checks if the definition adress anad the file adress matches)
            if defined_in == str(file_name.absolute()):
                yield value


# checks for the class it a dataclass
def check_for_dataclass(classes: Iterable[type]) -> Iterable[type]:
    for clazz in classes:
        if is_dataclass(clazz):
            yield clazz


def acess_all_folders_return_all_files(path_name: Path) -> list[str]:
    # acessing all files from the path directory that ends with .py
    return list(path_name.glob("**/*.py"))


# check for the path conains an init file or is it a python sript (ends with a .py) and returns the module name
def _map_the_thing(path_part: str) -> str:
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
        _map_the_thing(p) for p in path_to_file.relative_to(path_to_root_dir).parts
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

    list_validatons = []
    for x in all_data_classes:
        if issubclass(x, ValidatedModel) and x.__name__ != "ValidatedModel":
            list_validatons.append(x)

    for j in list_validatons:
        one = j._get_validations()
        field_names_validated = set(one.keys())
        field_names = {f.name for f in fields(j)}

        if field_names_validated != field_names:

            not_validated = field_names - field_names_validated
            print(
                f"In {j.__name__} ({inspect.getfile(j)}) you have not validated {', '.join(not_validated)}"
            )
            # print out all the class attribute names with a message to check validations for the class.
            # or even better to just print out the name of the variables that miss the validation
            # Altho simply printing out the class variable names should also work
            print(format(field_names))  # This returns empty
            exit(1)


if __name__ == "__main__":
    main()
