import inspect
import importlib
from typing import Iterable
import sys
from dataclasses import is_dataclass, fields

import csvcubed
from csvcubed.definitions import APP_ROOT_DIR_PATH
from pathlib import Path
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


def generate_modules(path_to_file: Path, path_to_root_dir: Path):

    path_parts = [
        _map_the_thing(p) for p in path_to_file.relative_to(path_to_root_dir).parts
    ]
    path_parts = ["csvcubed"] + [p for p in path_parts if p is not None]
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

    dict = {"": []}
    dict_keys = []
    for x in all_data_classes:
        if issubclass(x, ValidatedModel) and x.__name__ is not "ValidatedModel":
            testclass = x
            fornow = fields(x)
            dict_keys.append(x.__name__)
            dict[x.__name__] = [f.name for f in fornow]

    for z in dict_keys:
        print(f"class name : {z} \n")
        print(dict[z])
        print("\n \n")

    assert len(testclass._get_validations()) == len(fields(testclass))

    # create a validatemodell class
    # filter out the classes to get the subclasses of the validatedModel class with issubclass function
    # run _get_validation_errors()
    # do a comparison between the fields and the _get_validation_error() and if the to values don't match fail
    # in the reusablle-test.yaml file add in a run that will call this script and if it fails stop the build


if __name__ == "__main__":
    main()
