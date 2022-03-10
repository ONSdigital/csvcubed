"""
Config.json Loader
__________________

A loader for the config.json.
"""
import json
import logging

from pathlib import Path
from typing import Dict, Tuple, List

import pandas as pd
from jsonschema.exceptions import ValidationError
# import csvcubed.readers.v1_0.columnschema as v1_0_col_schema

from csvcubed.models.cube import *
from csvcubed.readers.v1_0.mapcolumntocomponent import map_column_to_qb_component \
    as v1_0_map_column_to_qb_component
from csvcubed.utils.dict import get_with_func_or_none
from csvcubed.utils.uri import uri_safe
from csvcubed.utils.json import load_json_from_uri, read_json_from_file
from csvcubed.utils.validators.schema import validate_dict_against_schema
from csvcubedmodels.rdf.namespaces import GOV


# Used to determine whether a column name matches accepted conventions
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


def _load_resource(resource_path: Path) -> dict:
    """
    Load a json schema document from either a File or URI
    """
    schema: dict = {}

    if resource_path.parts[0].startswith('http'):
        schema = load_json_from_uri(str(resource_path))

    else:
        if not resource_path.is_absolute():
            resource_path = resource_path.resolve()
        schema = read_json_from_file(resource_path)

    return schema


def _from_config_json_dict(
    data: pd.DataFrame, config: Optional[Dict], json_parent_dir: Path
) -> QbCube:
    columns: List[CsvColumn] = []
    metadata: CatalogMetadata = _metadata_from_dict(config)

    config_columns = config.get("columns", [])
    for column_title in config_columns:
        column_config = config_columns.get(column_title)

        # When the config json contains a col definition and the col title is not in the data
        column_data = (
            data[column_title] if column_title in data.columns else None
        )

        columns.append(
            v1_0_map_column_to_qb_component(
                column_title, column_config, column_data, json_parent_dir
            )
        )

    return Cube(metadata, data, columns)


def _metadata_from_dict(config: dict) -> "CatalogMetadata":
    creator = get_with_func_or_none(config, "creator", lambda c: str(GOV[uri_safe(c)]))
    publisher = get_with_func_or_none(
        config, "publisher", lambda p: str(GOV[uri_safe(p)])
    )
    themes = config.get("themes", "")
    if isinstance(themes, str) and themes:
        themes = [themes]
    keywords = config.get("keywords", "")
    if isinstance(keywords, str) and keywords:
        keywords = [keywords]

    return CatalogMetadata(
        identifier=config.get("id"),
        title=config.get("title"),
        description=config.get("description", ""),
        summary=config.get("summary", ""),
        creator_uri=creator,
        publisher_uri=publisher,
        public_contact_point_uri=config.get("public_contact_point"),
        dataset_issued=config.get("dataset_issued"),
        dataset_modified=config.get("dataset_modified"),
        license_uri=config.get("license"),
        theme_uris=[uri_safe(t) for t in themes if t]
        if isinstance(themes, list)
        else [],
        keywords=keywords if isinstance(keywords, list) else [],
        # spatial_bound_uri=uri_safe(config['spatial_bound'])
        #     if config.get('spatial_bound') else None,
        # temporal_bound_uri=uri_safe(config['temporal_bound'])
        #     if config.get('temporal_bound') else None,
        uri_safe_identifier_override=config["id"] if config.get("id") else None,
    )


def _read_and_check_csv(csv_path: Path) -> pd.DataFrame:
    """
    Reads the csv data file and performs rudimentary checks.
    """
    data = pd.read_csv(csv_path)

    if isinstance(data, pd.DataFrame):
        if data.shape[0] < 2:
            # Must have 2 or more rows, a heading row and a data row
            raise ValueError("CSV input must contain header row and at least one row of data")

    else:
        raise TypeError("There was a problem reading the csv file as a dataframe")

    return data


def get_cube_from_config_json(
    csv_path: Path, config_path: Optional[Path]
) -> Tuple[QbCube, List[ValidationError]]:
    """
    Generates a Cube structure from a config.json input.
    :return: tuple of cube and json schema errors (if any)
    """
    data = _read_and_check_csv(csv_path)

    # If we have a config json file then load it and validate against its reference schema
    if config_path:
        config = _load_resource(config_path.resolve())
        # Update loaded config's title if not defined, setting title from csv data file path.
        if config.get('title') is None:
            config['title'] = ' '.join(
                [word.capitalize() for word in csv_path.stem.replace('-', ' ').split(' ')]
            )
        schema = _load_resource(Path(config["$schema"]))
        schema_validation_errors = validate_dict_against_schema(
            value=config, schema=schema
        )

    # Create a default config, setting title from csv data file path.
    else:
        config = {'title': ' '.join(
            [word.capitalize() for word in csv_path.stem.replace('-',' ').split(' ')]
            )
        }
        schema_validation_errors = []

    parent_path = config_path.parent if config_path else csv_path.parent
    cube = _from_config_json_dict(data, config, parent_path)

    # Update metadata from csv where appropriate
    cube.metadata.title = (
        cube.metadata.title
        if cube.metadata.title
        else csv_path.name.upper().replace("_", " ")
    )

    # Update columns from csv where appropriate, i.e. config did not define the column
    config_column_titles = {col.csv_column_title for col in cube.columns}
    for i, column_title in enumerate(data.columns):
        # ... determine if the column_title in data matches a convention
        if column_title not in config_column_titles:
            convention_names = [
                standard_name
                for standard_name, options in CONVENTION_NAMES.items()
                if column_title.lower() in options
            ]

            # ... get or default the column type
            column_type = convention_names[0] if convention_names else "dimension"

            # ... create a default config dict for the column type
            if column_type == "dimension":
                column_dict = {
                    "type": column_type,
                    "label": column_title,
                    "code_list": True,
                }

            elif column_type == "observations":
                column_dict = {
                    "type": column_type,
                    "value": column_title,
                    "datatype": "decimal",
                }

            elif column_type in ["measures", "units"]:
                column_dict = {"type": column_type}
            elif column_type == "attribute":
                # Note: attribute type columns are currently not supported for getting from data
                raise ValueError(
                    "Column type 'Attribute' is not supported when using csv naming convention"
                )

            else:
                raise ValueError(f"Column type '{column_type}' is not supported.")

            try:
                qb_column: CsvColumn = v1_0_map_column_to_qb_component(
                    column_title=column_title,
                    column=column_dict,
                    data=data[column_title].astype("category"),
                    json_parent_dir=csv_path.parent.absolute(),
                )
                if i < len(cube.columns):
                    cube.columns.insert(i + 1, qb_column)
                else:
                    cube.columns.append(qb_column)

            except Exception as err:
                log.exception(f"{type(err)} exception raised because: {repr(err)}")
                raise err

    return cube, schema_validation_errors


if __name__ == "__main__":
    log.error(
        "The config deserialiser module should not be run directly, please user the 'csvcubed build' command."
    )
