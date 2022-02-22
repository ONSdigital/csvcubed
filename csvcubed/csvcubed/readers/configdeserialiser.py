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


# def _get_code_list(
#     column_label: str,
#     maybe_code_list: Optional[Union[bool, str]],
#     json_parent_dir: Path,
#     maybe_parent_uri: Optional[str],
#     column_data: PandasDataTypes,
#     maybe_property_value_url: Optional[str],
# ) -> Optional[QbCodeList]:
#
#     is_date_time_code_list = (
#         (
#             maybe_code_list is None
#             or (isinstance(maybe_code_list, bool) and maybe_code_list is True)
#         )
#         and maybe_parent_uri
#         == "http://purl.org/linked-data/sdmx/2009/dimension#refPeriod"
#         and maybe_property_value_url is not None
#         and maybe_property_value_url.startswith("http://reference.data.gov.uk/id/")
#     )
#
#     if is_date_time_code_list:
#         column_name_csvw_safe = csvw_column_name_safe(column_label)
#         columnar_data = pandas_input_to_columnar_str(column_data)
#         concepts = [
#             DuplicatedQbConcept(
#                 existing_concept_uri=uritemplate.expand(
#                     maybe_property_value_url, {column_name_csvw_safe: c}
#                 ),
#                 label=c,
#             )
#             for c in sorted(set(columnar_data))
#         ]
#         return CompositeQbCodeList(
#             CatalogMetadata(column_label),
#             concepts,
#         )
#
#     elif maybe_code_list is not None:
#         if isinstance(maybe_code_list, str):
#             return ExistingQbCodeList(maybe_code_list)
#
#         #elif isinstance(maybe_code_list, bool) and not maybe_code_list:
#         elif isinstance(maybe_code_list, bool) and maybe_code_list is False:
#             return None
#
#         else:
#             raise Exception(f"Unexpected codelist value '{maybe_code_list}'")
#
#     return NewQbCodeListInCsvW(
#         json_parent_dir
#         / "codelists"
#         / f"{uri_safe(column_label)}.csv-metadata.json"
#     )


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
    # columns: List[CsvColumn] = _columns_from_config_json(d.get("columns", []), data, json_parent_dir)
    columns: List[QbColumn] = []
    for column_title in d.get('columns', []):
        column_config = d['columns'].get(column_title)
        columns.append(map_column_to_qb_component(column_title, column_config,
                                                  data[column_title], json_parent_dir))

    return Cube(metadata, data, columns)


# def _override_config_for_cube_id(config: dict, cube_id: str) -> Optional[dict]:
#     """
#     Apply cube config overrides contained inside the `cubes` dictionary to get the config for the given `cube_id`
#     """
#     # Need to do a deep-clone of the config to avoid side-effecs
#     config = copy.deepcopy(config)
#
#     config_json_id = config.get("id")
#     if config_json_id is not None and config_json_id == cube_id:
#         if "cubes" in config:
#             del config["cubes"]
#
#         return config
#     elif "cubes" in config and cube_id in config["cubes"]:
#         overrides = config["cubes"][cube_id]
#         for k, v in overrides.items():
#             config[k] = v
#
#         return config
#     else:
#         return None


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

    summary: Optional[str] = field(default=None, repr=False)
    landing_page_uris: list[str] = field(default_factory=list, repr=False)
    dataset_issued: Optional[datetime] = field(default=None, repr=False)
    dataset_modified: Optional[datetime] = field(default=None, repr=False)
    license_uri: Optional[str] = field(default=None, repr=False)
    public_contact_point_uri: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)
    spatial_bound_uri: Optional[str] = field(default=None, repr=False)
    temporal_bound_uri: Optional[str] = field(default=None, repr=False)




# def _columns_from_config_json(column_mappings: Dict[str, Any],
#                               data: pd.DataFrame,
#                               json_parent_dir: Path
#                               ) -> List[CsvColumn]:
#
#     defined_columns: List[CsvColumn] = []
#
#     column_titles_in_data: List[str] = [
#         str(title) for title in data.columns  # type: ignore
#     ]
#     for col_title in column_titles_in_data:
#         maybe_config = column_mappings.get(col_title)
#         defined_columns.append(
#             _get_column_for_metadata_config(
#                 col_title, maybe_config, data[col_title], json_parent_dir
#             )
#         )
#
#     columns_missing_in_data = set(column_mappings.keys()) - set(column_titles_in_data)
#     for col_title in columns_missing_in_data:
#         config = column_mappings[col_title]
#         defined_columns.append(
#             _get_column_for_metadata_config(
#                 col_title, config, pd.Series([]), json_parent_dir
#             )
#         )
#
#     return defined_columns


# def _get_column_for_metadata_config(
#     column_name: str,
#     col_config: Optional[Union[dict, bool]],
#     column_data: PandasDataTypes,
#     json_parent_dir: Path,
# ) -> CsvColumn:
#     if isinstance(col_config, dict):
#         # The schema defines 'type' as a required property, however if absent we can set to
#         # 'dimension' ?
#             # if col_config.get("type") is None:
#             #     col_config['type'] = 'dimension'
#             #
#             # return map_column_to_qb_component(
#             #     column_name, col_config, column_data, json_parent_dir
#             # )
#         # end
#
#         if col_config.get("type") is not None:
#             return map_column_to_qb_component(
#                 column_name, col_config, column_data, json_parent_dir
#             )
#         csv_safe_column_name = csvw_column_name_safe(column_name)
#
#         # maybe_dimension_uri = col_config.get("dimension")
#         maybe_property_value_url = col_config.get("value")
#         # maybe_parent_uri = col_config.get("parent")
#         maybe_parent_uri = col_config.get("from_existing")
#         maybe_description = col_config.get("description")
#         maybe_label = col_config.get("label")
#         # maybe_attribute_uri = col_config.get("attribute")
#         maybe_unit_uri = col_config.get("unit")
#         maybe_measure_uri = col_config.get("measure")
#         maybe_data_type = col_config.get("data_type")
#
#         # if maybe_dimension_uri is not None and maybe_property_value_url is not None:
#         #     if maybe_dimension_uri == "http://purl.org/linked-data/cube#measureType":
#         #         # multi-measure cube
#         #         defined_measure_types: List[str] = col_config.get("types", [])
#         #         if maybe_property_value_url is not None:
#         #             defined_measure_types = [
#         #                 uritemplate.expand(
#         #                     maybe_property_value_url, {csv_safe_column_name: d}
#         #                 )
#         #                 for d in defined_measure_types
#         #             ]
#         #
#         #         if len(defined_measure_types) == 0:
#         #             raise Exception(
#         #                 f"Property 'types' was not defined in measure types column '{column_name}'."
#         #             )
#         #
#         #         measures = QbMultiMeasureDimension(
#         #             [ExistingQbMeasure(t) for t in defined_measure_types]
#         #         )
#         #         return QbColumn(column_name, measures, maybe_property_value_url)
#         #     else:
#         #         return QbColumn(
#         #             column_name,
#         #             ExistingQbDimension(maybe_dimension_uri),
#         #             maybe_property_value_url,
#         #         )
#         # elif (
#         if (
#             maybe_parent_uri is not None
#             or maybe_description is not None
#             or maybe_label is not None
#         ):
#             # label: str = column_name if maybe_label is None else maybe_label
#             label: str = maybe_label
#             code_list = _get_code_list(
#                 label,
#                 col_config.get("code_list"),
#                 json_parent_dir,
#                 maybe_parent_uri,
#                 column_data,
#                 maybe_property_value_url,
#             )
#             new_dimension = NewQbDimension(
#                 label,
#                 description=maybe_description,
#                 parent_dimension_uri=maybe_parent_uri,
#                 source_uri=col_config.get("source"),
#                 code_list=code_list,
#             )
#             csv_column_value_url_template = (
#                 None
#                 if isinstance(code_list, CompositeQbCodeList)
#                 else maybe_property_value_url
#             )
#             return QbColumn(
#                 column_name,
#                 new_dimension,
#                 csv_column_value_url_template,
#             )
#         # elif maybe_attribute_uri is not None and maybe_property_value_url is not None:
#         #     if (
#         #         maybe_attribute_uri
#         #         == "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
#         #     ):
#         #         distinct_unit_uris = [
#         #             uritemplate.expand(
#         #                 maybe_property_value_url, {csv_safe_column_name: u}
#         #             )
#         #             for u in set(pandas_input_to_columnar_str(column_data))
#         #         ]
#         #         dsd_component = QbMultiUnits(
#         #             [ExistingQbUnit(u) for u in distinct_unit_uris]
#         #         )
#         #     else:
#         #         dsd_component = ExistingQbAttribute(maybe_attribute_uri)
#         #
#         #     return QbColumn(column_name, dsd_component, maybe_property_value_url)
#         elif maybe_unit_uri is not None and maybe_measure_uri is not None:
#             measure_component = ExistingQbMeasure(maybe_measure_uri)
#             unit_component = ExistingQbUnit(maybe_unit_uri)
#             observation_value = QbSingleMeasureObservationValue(
#                 measure=measure_component,
#                 unit=unit_component,
#                 data_type=maybe_data_type or "decimal",
#             )
#             return QbColumn(column_name, observation_value)
#         elif maybe_data_type is not None:
#             return QbColumn(
#                 column_name, QbMultiMeasureObservationValue(maybe_data_type)
#             )
#         else:
#             raise Exception(f"Unmatched column definition: {col_config}")
#
#     elif isinstance(col_config, bool) and col_config:
#         return SuppressedCsvColumn(column_name)
#     else:
#         # If not a known/expected type/value (or is a string), treat it as a dimension.
#         maybe_description: Optional[str] = None
#         if isinstance(col_config, str):
#             maybe_description = col_config
#
#         new_dimension = NewQbDimension.from_data(
#             column_name, column_data, description=maybe_description
#         )
#         return QbColumn(column_name, new_dimension)


def get_cube_from_data(csv_path: Path, data: PandasDataTypes) -> QbCube:
    """
    Given a Pandas DataFrame, it resolves each column to a column based on naming conventions
    The cube must have dimension, observation, units and measures columns
    The csv_path arg is used for the Cube title
    """
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
        data: pd.DataFrame
) -> Tuple[QbCube, List[ValidationError]]:
    """
    Generates a Cube structure from a config.json input.
    :return: tuple of cube and json schema errors (if any)
    """

    config = _load_resource(config_path)
    schema_path = Path("..", "..", "..", "..", "csvcubed", "schema", "cube-config-schema.json").resolve()
    schema = _load_resource(schema_path)
    try:
        errors = validate_dict_against_schema(value=config, schema=schema)
        if errors:
            return None, errors

    except Exception as err:
        print(err)

    return _from_config_json_dict(config, data, config_path.parent), None


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
    data: pd.DataFrame = pd.read_csv(csv_path)

    if config_path:
        cube, json_schema_validation_errors = get_cube_from_config_json(config_path, data)

    else:
        cube, json_schema_validation_error = get_cube_from_data(csv_path, data)

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
