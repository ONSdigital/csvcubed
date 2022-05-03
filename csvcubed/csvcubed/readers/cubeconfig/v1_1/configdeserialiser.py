"""
Config.json Loader
__________________

A loader for the config.json.
"""
import datetime
import logging
from json import JSONDecodeError

from pathlib import Path
from typing import Dict, Tuple, List, Callable
from dateutil import parser

import pandas as pd
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pandas import DataFrame

from csvcubed.models.cube import *
from csvcubed.models.validationerror import ValidationError
from .mapcolumntocomponent import map_column_to_qb_component
from csvcubed.utils.dict import get_with_func_or_none
from csvcubed.utils.iterables import first
from csvcubed.utils.pandas import read_csv
from csvcubed.utils.uri import uri_safe
from csvcubed.utils.validators.schema import validate_dict_against_schema
from csvcubed.readers.cubeconfig.utils import load_resource

# Used to determine whether a column name matches accepted conventions
from ...preconfiguredtemplates import apply_preconfigured_values_from_template

CONVENTION_NAMES = {
    "measures": {
        "measure",
        "measures",
        "measures column",
        "measure column",
        "measure type",
        "measure types",
    },
    "observations": {
        "observation",
        "observations",
        "obs",
        "values",
        "value",
        "val",
        "vals",
    },
    "units": {
        "unit",
        "units",
        "units column",
        "unit column",
        "unit type",
        "unit types",
    },
}

log = logging.getLogger(__name__)


def get_deserialiser(
    schema_path: str, version_module_path: str
) -> Callable[
    [Path, Optional[Path]],
    Tuple[QbCube, List[JsonSchemaValidationError], List[ValidationError]],
]:
    """Generates a deserialiser function which validates the JSON file against the schema at :obj:`schema_path`"""

    def get_cube_from_config_json(
        csv_path: Path, config_path: Optional[Path]
    ) -> Tuple[QbCube, List[JsonSchemaValidationError], List[ValidationError]]:
        """
        Generates a Cube structure from a config.json input.
        :return: tuple of cube and json schema errors (if any)
        """
        data, data_errors = _read_and_check_csv(csv_path)

        # If we have a config json file then load it and validate against its reference schema
        if config_path:
            config = load_resource(config_path.resolve())
            # Update loaded config's title if not defined, setting title from csv data file path.
            if config.get("title") is None:
                config["title"] = _generate_title_from_file_name(csv_path)
            try:
                schema = load_resource(schema_path)
                schema_validation_errors = validate_dict_against_schema(
                    value=config, schema=schema
                )
            except JSONDecodeError as err:
                log.warning(
                    "Validation of the config json is not currently available, continuing without validation."
                )
                schema_validation_errors = []

        # Create a default config, setting title from csv data file path.
        else:
            config = {"title": _generate_title_from_file_name(csv_path)}
            schema_validation_errors = []

        cube = _get_cube_from_config_json_dict(data, config, version_module_path)

        _configure_remaining_columns_by_convention(cube, data)

        return cube, schema_validation_errors, data_errors

    return get_cube_from_config_json


def _get_cube_from_config_json_dict(
    data: pd.DataFrame, config: Dict, version_module_path: str
) -> QbCube:
    columns: List[CsvColumn] = []
    metadata: CatalogMetadata = _metadata_from_dict(config)

    config_columns = config.get("columns", {})
    for (column_title, column_config) in config_columns.items():
        columns.append(
            _get_qb_column_from_json(
                column_config, column_title, data, version_module_path
            )
        )

    return Cube(metadata, data, columns)


def _get_qb_column_from_json(
    column_config: dict, column_title: str, data: pd.DataFrame, version_module_path: str
):
    # When the config json contains a col definition and the col title is not in the data
    column_data = data[column_title] if column_title in data.columns else None
    # Load configuration from the "from_template": if provided.
    apply_preconfigured_values_from_template(
        column_config=column_config,
        version_module_path=version_module_path,
        column_name=column_title,
    )
    return map_column_to_qb_component(column_title, column_config, column_data)


def _parse_iso_8601_date_time(
    date_or_date_time: str,
) -> Union[datetime.date, datetime.datetime]:
    dt = parser.isoparse(date_or_date_time)
    if dt.time() == datetime.time.min:
        return dt.date()

    return dt


def _metadata_from_dict(config: dict) -> "CatalogMetadata":
    themes = config.get("themes", [])
    if themes and isinstance(themes, str):
        themes = [themes]

    keywords = config.get("keywords", [])
    if keywords and isinstance(keywords, str):
        keywords = [keywords]

    return CatalogMetadata(
        identifier=get_with_func_or_none(config, "id", uri_safe),
        title=config["title"],
        description=config.get("description", ""),
        summary=config.get("summary", ""),
        creator_uri=config.get("creator"),
        publisher_uri=config.get("publisher"),
        public_contact_point_uri=config.get("public_contact_point"),
        dataset_issued=get_with_func_or_none(
            config, "dataset_issued", _parse_iso_8601_date_time
        ),
        dataset_modified=get_with_func_or_none(
            config, "dataset_modified", _parse_iso_8601_date_time
        ),
        license_uri=config.get("license"),
        theme_uris=themes,
        keywords=keywords,
        # spatial_bound_uri=uri_safe(config['spatial_bound'])
        #     if config.get('spatial_bound') else None,
        # temporal_bound_uri=uri_safe(config['temporal_bound'])
        #     if config.get('temporal_bound') else None,
    )


def _read_and_check_csv(csv_path: Path) -> Tuple[DataFrame, List[ValidationError]]:
    """
    Reads the csv data file and performs rudimentary checks.
    """
    data, data_errors = read_csv(csv_path)

    if isinstance(data, pd.DataFrame):
        if data.shape[0] < 2:
            # Must have 2 or more rows, a heading row and a data row
            raise ValueError(
                "CSV input must contain header row and at least one row of data"
            )

    else:
        raise TypeError("There was a problem reading the csv file as a dataframe")

    return data, data_errors


def _configure_remaining_columns_by_convention(
    cube: QbCube, data: pd.DataFrame
) -> None:
    """Update columns from csv where appropriate, i.e. config did not define the column."""
    configured_columns = {col.csv_column_title: col for col in cube.columns}
    ordered_columns: List[CsvColumn] = []
    for i, column_title in enumerate(data.columns):
        # ... determine if the column_title in data matches a convention
        if column_title in configured_columns:
            ordered_columns.append(configured_columns[column_title])
            del configured_columns[column_title]
        elif column_title not in configured_columns:
            column_dict = _get_conventional_column_definition_for_title(column_title)

            qb_column: CsvColumn = map_column_to_qb_component(
                column_title=column_title,
                column=column_dict,
                data=data[column_title].astype("category"),
            )

            ordered_columns.append(qb_column)

    cube.columns = ordered_columns + list(configured_columns.values())


def _get_conventional_column_definition_for_title(column_title: str) -> dict:
    matching_column_types = [
        standard_name
        for standard_name, options in CONVENTION_NAMES.items()
        if column_title.lower() in options
    ]
    # ... get or default the column type
    column_type = first(matching_column_types) or "dimension"
    # ... create a default config dict for the column type
    if column_type == "dimension":
        return {
            "type": column_type,
            "label": column_title,
            "code_list": True,
        }

    elif column_type == "observations":
        return {
            "type": column_type,
            "value": column_title,
            "datatype": "decimal",
        }

    elif column_type in ["measures", "units"]:
        return {"type": column_type}
    elif column_type == "attribute":
        # Note: attribute type columns are currently not supported for getting from data
        raise ValueError(
            "Conventionally named attribute columns are not current supported"
        )

    raise ValueError(f"Column type '{column_type}' is not supported.")


def _generate_title_from_file_name(csv_path: Path) -> str:
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
