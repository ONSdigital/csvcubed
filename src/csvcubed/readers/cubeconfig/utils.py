from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from pandas import DataFrame
from csvcubed.definitions import APP_ROOT_DIR_PATH

from csvcubed.models.validationerror import ValidationError
from csvcubed.utils.json import load_json_document
from csvcubed.utils.pandas import read_csv
from csvcubed.utils.uri import looks_like_uri


def load_resource(resource_path: Union[str, Path]) -> dict:
    """
    Loads a json schema document from either a File or URI
    """
    if isinstance(resource_path, str):
        if looks_like_uri(resource_path):
            return load_json_document(str(resource_path))
        else:
            resource_path = Path(resource_path)

    if not resource_path.is_absolute():
        resource_path = resource_path.resolve()
    return load_json_document(resource_path)


def generate_title_from_file_name(csv_path: Path) -> str:
    """
    Formats a file Path, stripping -_ and returning the capitalised file name without extn
    e.g. Path('./csv-data_file.csv') -> 'Csv Data File'
    """
    return " ".join(
        [
            word.capitalize()
            for word in csv_path.stem.replace("-", " ").replace("_", " ").split(" ")
        ]
    )


def read_and_check_csv(
    csv_path: Path, dtype: Optional[Dict[str, str]] = None
) -> Tuple[DataFrame, List[ValidationError]]:
    """
    Reads the csv data file and performs rudimentary checks.
    """

    data, data_errors = read_csv(csv_path, dtype=dtype)

    if isinstance(data, DataFrame):
        if len(data) == 0:
            # Must have 2 or more rows, a heading row and a data row
            raise ValueError(
                "CSV input must contain header row and at least one row of data "
            )
    else:
        raise TypeError("There was a problem reading the csv file as a dataframe")

    return data, data_errors


def get_url_to_file_path_map() -> Dict[str, Path]:

    map_uri_to_file_path = {
        "//purl.org/csv-cubed/qube-config/v1.0": APP_ROOT_DIR_PATH
        / "schema"
        / "cube-config"
        / "v1_0"
        / "schema.json",
        "//purl.org/csv-cubed/qube-config/v1.1": APP_ROOT_DIR_PATH
        / "schema"
        / "cube-config"
        / "v1_1"
        / "schema.json",
        "//purl.org/csv-cubed/qube-config/v1.2": APP_ROOT_DIR_PATH
        / "schema"
        / "cube-config"
        / "v1_2"
        / "schema.json",
        "//purl.org/csv-cubed/qube-config/v1.3": APP_ROOT_DIR_PATH
        / "schema"
        / "cube-config"
        / "v1_3"
        / "schema.json",
        "//purl.org/csv-cubed/qube-config/v1.4": APP_ROOT_DIR_PATH
        / "schema"
        / "cube-config"
        / "v1_4"
        / "schema.json",
        "//purl.org/csv-cubed/qube-config/v1": APP_ROOT_DIR_PATH
        / "schema"
        / "cube-config"
        / "v1_4"
        / "schema.json",  # v1 defaults to latest minor version of v1.*.
        "//purl.org/csv-cubed/codelist-config/v1.0": APP_ROOT_DIR_PATH
        / "schema"
        / "codelist-config"
        / "v1_0"
        / "schema.json",
        "//purl.org/csv-cubed/codelist-config/v1.1": APP_ROOT_DIR_PATH
        / "schema"
        / "codelist-config"
        / "v1_1"
        / "schema.json",
        "//purl.org/csv-cubed/code-list-config/v1": APP_ROOT_DIR_PATH
        / "schema"
        / "codelist-config"
        / "v1_1"
        / "schema.json",  # v1 defaults to latest minor version of v1.*.
    }

    templates_dir = APP_ROOT_DIR_PATH / "readers" / "cubeconfig" / "v1_0" / "templates"

    template_files = templates_dir.rglob("**/*.json*")

    if not any(template_files):
        raise ValueError(f"Couldn't find template files in {templates_dir}.")

    for template_file in template_files:
        relative_file_path = str(template_file.relative_to(templates_dir))
        uri = (
            "//raw.githubusercontent.com/GSS-Cogs/csvcubed/main/src/csvcubed/readers/cubeconfig/v1_0/templates/"
            + relative_file_path
        )
        map_uri_to_file_path[uri] = template_file

    return map_uri_to_file_path