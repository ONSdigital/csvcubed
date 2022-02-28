"""
Config.json Loader
__________________

A loader for the config.json.
"""
import json
import logging

from typing import Dict, Tuple

from urllib.parse import urlsplit

import pandas as pd
from jsonschema.exceptions import ValidationError
from csvcubed.readers.v1_0.columnschema import *

from csvcubed.inputs import PandasDataTypes
from csvcubed.models.cube import *
from csvcubed.readers.v1_0.mapcolumntocomponent import map_column_to_qb_component
from csvcubed.utils.dict import get_from_dict_ensure_exists, get_with_func_or_none
from csvcubed.utils.uri import uri_safe
from csvcubed.utils.json import load_json_from_uri, read_json_from_file
from csvcubed.utils.validators.schema import validate_dict_against_schema
from csvcubed.utils.qb.validation.cube import validate_qb_component_constraints
from csvcubedmodels.rdf.namespaces import GOV



# Used to determine whether a column name matches accepted conventions
CONVENTION_NAMES = {
    "measures": [
        "measure",
        "measures",
        "measures column",
        "measure column",
        "measure type",
        "measure types",
    ],
    "observations": [
        "observation",
        "observations",
        "obs",
        "values",
        "value",
        "val",
        "vals",
    ],
    "units": ["unit", "units", "units column", "unit column", "unit type", "unit types"]
    # 'attribute': ['attribute', 'attributes']  # Not supported for loading cube from convention only.
}

log = logging.getLogger(__name__)


def _load_resource(resource_path: Path) -> dict:
    """
    Load a json schema document from either a File or URI
    """
    schema: dict = {}

    if "http" in urlsplit(str(resource_path)).scheme:
        schema = load_json_from_uri(resource_path)

    else:
        schema = read_json_from_file(resource_path)

    return schema


def initialise_from_config(self, config_json: dict) -> bool:
    """
    Initialises a Qube from a qube json file.

    param: config_json: A Qube created according to a Qube Config schema
    """


def _override_catalog_metadata_state(
    catalog_metadata_json_file: Path, cube: QbCube
) -> None:
    with open(catalog_metadata_json_file, "r") as f:
        catalog_metadata_dict: dict = json.load(f)
    overriding_catalog_metadata = CatalogMetadata.from_dict(catalog_metadata_dict)
    cube.metadata.override_with(
        overriding_catalog_metadata,
        overriding_keys={k for k in catalog_metadata_dict.keys()},
    )


def _from_config_json_dict(d: Dict,
                           data: pd.DataFrame,
                           json_parent_dir: Path
                          ) -> QbCube:

    metadata: CatalogMetadata = _metadata_from_dict(d)
    columns: List[QbColumn] = []
    for column_title in d.get('columns', []):
        column_config = d['columns'].get(column_title)
        columns.append(map_column_to_qb_component(column_title, column_config,
                                                  data[column_title], json_parent_dir))

    return Cube(metadata, data, columns)


def _metadata_from_dict(config: dict) -> "CatalogMetadata":
    creator = get_with_func_or_none(config, "creator", lambda c: str(GOV[uri_safe(c)]))
    publisher = get_with_func_or_none(config, "publisher", lambda p: str(GOV[uri_safe(p)]))
    themes = config.get('themes', "")
    if isinstance(themes, str) and themes:
        themes = [themes]
    keywords = config.get('keywords', "")
    if isinstance(keywords, str) and keywords:
        keywords = [keywords]

    return CatalogMetadata(
        identifier=config.get("id"),
        title=get_from_dict_ensure_exists(config, "title"),
        description=config.get("description", ""),
        creator_uri=creator,
        publisher_uri=publisher,
        theme_uris=[uri_safe(t) for t in themes if t] if isinstance(themes, list) else None,
        keywords=keywords if isinstance(keywords, list) else None,
        spatial_bound_uri=uri_safe(config['spatial_bound'])
            if config.get('spatial_bound') else None,
        temporal_bound_uri=uri_safe(config['temporal_bound'])
            if config.get('temporal_bound') else None,
        uri_safe_identifier_override=config['id'] if config.get('id') else None
    )


def get_cube_from_data(csv_path: Path) -> QbCube:
    """
    Given a Pandas DataFrame, it resolves each column to a column based on naming conventions
    The cube must have dimension, observation, units and measures columns
    The csv_path arg is used for the Cube title
    """
    data: pd.DataFrame = pd.read_csv(csv_path)
    if data.shape[0] < 2:
        # Must have 2 or more rows, a heading row and a data row
        raise ValueError("The csv data did not contain sufficient rows to continue")

    elif data.shape[1] < 3:
        # Must have 3 or more columns, 1+ dimension, 1 observation, 1 attribute,
        raise ValueError("The csv did not contain sufficient columns to continue")

    # Iterate over the column names and count the type for each
    convention_col_counts = {
        "dimension": 0,
        "observations": 0,
        "measures": 0,
        "units": 0,
        "attribute": 0,
    }
    cube_columns: List[QbColumn] = []
    column_types: List[str] = []
    for i, column_name in enumerate(data.columns):
        # Determine column type by matching column names accepted by convention or default to 'dimension'
        convention_name_matches = [
            standard_name
            for standard_name, options in CONVENTION_NAMES.items()
            if column_name.lower() in options
        ]
        column_type = (
            convention_name_matches[0] if convention_name_matches else "dimension"
        )
        column_types.append(column_type)
        convention_col_counts[column_type] += 1

    #  Check we have the pre-requisite columns
    if convention_col_counts["dimension"] < 1:
        raise ValueError("The data does not contain any dimension columns")
    if convention_col_counts["observations"] < 1:
        raise ValueError("The data does not contain any observation columns")
    if convention_col_counts["attribute"] < 0:
        raise ValueError("The data does not contain any attribute columns")
    if convention_col_counts["measures"] < 1:
        raise ValueError("The data does not contain any measure columns")
    if convention_col_counts["units"] < 1:  # needs resolving between Rob and Andrew
        raise ValueError("The data does not contain any attribute columns")

    for i, column_type in enumerate(column_types):
        # Build a dict of fields for the identified column types' data-class
        column_name = data.columns[i]
        column_data = data.T.iloc[i]

        if column_type == "dimension":
            column_dict = {
                "type": column_type,
                "label": column_name,
                "code_list": True
            }

        elif column_type == "observations":
            column_dict = {
                "type": column_type,
                "value": column_name,
                "datatype": "decimal",
            }

        elif column_type in ["measures", "units"]:
            column_dict = {
                "type": column_type
            }
        elif column_type == "attribute":
            # Note: attribute type columns are currently not supported
            raise ValueError(
                "Column type 'Attribute' is not supported when using csv naming convention"
            )

        else:
            raise ValueError(f"Column type '{column_type}' is not supported.")

        # As all columns will be new in this scenario get a pd.Series for the column

        try:
            qb_column = map_column_to_qb_component(
                column_title=column_name,
                column=column_dict,
                data=column_data.astype("category"),
                json_parent_dir=csv_path.parent.absolute(),
            )
            cube_columns.append(qb_column)

        except Exception as err:
            import traceback
            traceback.print_exc()
            log.error(f"{type(err)} exception raised because: {repr(err)}")

    cube_metadata = _metadata_from_dict(
        {"id": str(csv_path).upper(), "title": csv_path.name.upper().replace("_", " ")}
    )
    # TODO - Create the new Cube
    cube = Cube(metadata=cube_metadata, data=data, columns=cube_columns)
    # validation_errors = cube.validate()
    validation_errors = cube.pydantic_validation()

    return cube, validation_errors


def get_cube_from_config_json(
        config_path: Path,
        csv_path: Path
) -> Tuple[QbCube, List[ValidationError]]:
    """
    Generates a Cube structure from a config.json input.
    :return: tuple of cube and json schema errors (if any)
    """
    data: pd.DataFrame = pd.read_csv(csv_path)
    config = _load_resource(config_path.resolve())
    schema = _load_resource(Path(config['$schema']).resolve())
    try:
        errors = validate_dict_against_schema(value=config, schema=schema)
        if errors:
            return None, errors

    except Exception as err:
        print(err)

    return _from_config_json_dict(config, data, config_path.parent), []


def build(
    csv_path: Path,
    config_path: Optional[Path] = None,
    # catalog_metadata_json_file: Optional[Path]
    # output_directory: Path,
    # csv_path: Path,
    # fail_when_validation_error_occurs: bool,
    # validation_errors_file_out: Optional[Path],
):
    # print(f"{Style.DIM}CSV: {csv_path.absolute()}")
    # print(f"{Style.DIM}info.json: {config_json.absolute()}")
    # data: pd.DataFrame = pd.read_csv(csv_path)

    if config_path:
        cube, json_schema_validation_errors = get_cube_from_config_json(config_path, csv_path)

    else:
        cube, json_schema_validation_error = get_cube_from_data(csv_path, csv_path)

    # if catalog_metadata_json_file is not None:
    #     _override_catalog_metadata_state(catalog_metadata_json_file, cube)

    validation_errors = cube.validate()
    validation_errors += validate_qb_component_constraints(cube)
    print(f"validation_errors:{validation_errors}")

    # if not output_directory.exists():
    #     print(f"Creating output directory {output_directory.absolute()}")
    #     output_directory.mkdir()

    # if len(validation_errors) > 0 or len(json_schema_validation_errors) > 0:
    #     for error in validation_errors:
    #         print(
    #             f"{Fore.RED + Style.BRIGHT}Validation Error: {Style.NORMAL + error.message}"
    #         )
    #
    #     for err in json_schema_validation_errors:
    #         print(
    #             f"{Fore.LIGHTRED_EX + Style.BRIGHT}Schema Validation Error: {Style.NORMAL + err.message}"
    #         )
    #
    #     if validation_errors_file_out is not None:
    #         validation_errors_dict = [
    #             e.as_json_dict()
    #             if isinstance(e, DataClassBase)
    #             else dataclasses.asdict(e)
    #             for e in validation_errors
    #         ]
    #         all_errors = validation_errors_dict + [
    #             e.message for e in json_schema_validation_errors
    #         ]
    #
    #         with open(validation_errors_file_out, "w+") as f:
    #             json.dump(all_errors, f, indent=4)
    #
    #     if fail_when_validation_error_occurs and len(validation_errors) > 0:
    #         exit(1)
    #
    # qb_writer = QbWriter(cube)
    # qb_writer.write(output_directory)

    print(f"Build Complete")
    return cube, validation_errors


if __name__ == "__main__":
    log.error(
        "The config deserialiser module should not be run directly, please user the 'csvcubed build' command."
    )
