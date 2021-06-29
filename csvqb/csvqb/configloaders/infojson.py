from typing import Dict, List, Any, Optional, Union, Set
from pathlib import Path
import json
import copy

import pandas as pd

from csvqb.models.cube.cube import Cube, CubeMetadata
from csvqb.models.cube.columns import CsvColumn, SuppressedCsvColumn
from csvqb.models.cube.qb.columns import QbColumn
from csvqb.models.cube.qb.components.observedvalue import QbSingleMeasureObservationValue, \
    QbMultiMeasureObservationValue
from csvqb.models.cube.qb.components.dimension import NewQbDimension, ExistingQbDimension
from csvqb.models.cube.qb.components.measure import ExistingQbMeasure, QbMultiMeasureDimension
from csvqb.models.cube.qb.components.attribute import ExistingQbAttribute
from csvqb.models.cube.qb.components.unit import ExistingQbUnit

from csvqb.models.cube.qb.components.codelist import ExistingQbCodeList, NewQbCodeList
from csvqb.utils.qb.cube import validate_qb_component_constraints


def get_cube_from_info_json(info_json: Path, data: pd.DataFrame, cube_id: Optional[str] = None) -> Cube:
    with open(info_json, "r") as f:
        config = json.load(f)

    if cube_id is not None:
        config = _override_config_for_cube_id(config, cube_id)

    if config is None:
        raise Exception(f"Config not found for cube with id '{cube_id}'")

    cube = _from_info_json_dict(config, data)
    validation_errors = validate_qb_component_constraints(cube)
    for error in validation_errors:
        # todo: Do something better with errors?
        print(f"ERROR: {error.message}")

    return cube


def _override_config_for_cube_id(config: dict, cube_id: str) -> Optional[dict]:
    """
        Apply cube config overrides contained inside the `cubes` dictionary to get the config for the given `cube_id`
    """
    # Need to do a deep-clone of the config to avoid side-effecs
    config = copy.deepcopy(config)

    info_json_id = config.get("id")
    if info_json_id is not None and info_json_id == cube_id:
        if "cubes" in config:
            del config["cubes"]

        return config
    elif "cubes" in config and cube_id in config["cubes"]:
        overrides = config["cubes"][cube_id]
        for k, v in overrides.items():
            config[k] = v

        return config
    else:
        return None


def _from_info_json_dict(d: Dict, data: pd.DataFrame):
    metadata = CubeMetadata.from_dict(d)
    transform_section = d.get("transform", {})
    columns = _columns_from_info_json(transform_section.get("columns", []), data)

    return Cube(metadata, data, columns)


def _columns_from_info_json(column_mappings: Dict[str, Any], data: pd.DataFrame) -> List[CsvColumn]:
    defined_columns: List[CsvColumn] = []

    for col_title in data.columns:
        maybe_config = column_mappings.get(col_title)
        defined_columns.append(_get_column_for_metadata_config(col_title, maybe_config, data[col_title]))

    return defined_columns


def _get_column_for_metadata_config(column_name: str, col_config: Optional[Union[dict, bool]],
                                    column_data: pd.Series) -> CsvColumn:
    if isinstance(col_config, dict):
        maybe_dimension_uri = col_config.get("dimension")
        maybe_property_value_url = col_config.get("value")
        maybe_parent_uri = col_config.get("parent")
        maybe_description = col_config.get("description")
        maybe_label = col_config.get("label")
        maybe_attribute_uri = col_config.get("attribute")
        maybe_unit_uri = col_config.get("unit")
        maybe_measure_uri = col_config.get("measure")
        maybe_data_type = col_config.get("datatype")

        if maybe_dimension_uri is not None and maybe_property_value_url is not None:
            if maybe_dimension_uri == "http://purl.org/linked-data/cube#measureType":
                # multi-measure cube
                defined_measure_types: List[str] = col_config.get("types", [])
                if len(defined_measure_types) == 0:
                    raise Exception(f"Property 'types' was not defined in measure types column '{column_name}'.")

                measures = QbMultiMeasureDimension([ExistingQbMeasure(t) for t in defined_measure_types])
                return QbColumn(column_name, measures, maybe_property_value_url)
            else:
                return QbColumn(column_name, ExistingQbDimension(maybe_dimension_uri), maybe_property_value_url)
        elif maybe_parent_uri is not None or maybe_description is not None or maybe_label is not None:
            label: str = column_name if maybe_label is None else maybe_label
            code_list = _get_code_list(label, col_config.get("codelist"), column_data)
            new_dimension = NewQbDimension(label,
                                           description=maybe_description,
                                           parent_dimension_uri=maybe_parent_uri,
                                           source_uri=col_config.get("source"),
                                           code_list=code_list)
            return QbColumn(column_name, new_dimension, maybe_property_value_url)
        elif maybe_attribute_uri is not None and maybe_property_value_url is not None:
            return QbColumn(column_name, ExistingQbAttribute(maybe_attribute_uri))
        elif maybe_unit_uri is not None and maybe_measure_uri is not None:
            measure_component = ExistingQbMeasure(maybe_measure_uri)
            unit_component = ExistingQbUnit(maybe_unit_uri)
            observation_value = QbSingleMeasureObservationValue(measure_component, unit_component, maybe_data_type)
            return QbColumn(column_name, observation_value)
        elif maybe_data_type is not None:
            return QbColumn(column_name, QbMultiMeasureObservationValue(maybe_data_type))
        else:
            raise Exception(f"Unmatched column definition: {col_config}")
    elif isinstance(col_config, bool) and col_config:
        return SuppressedCsvColumn(column_name)
    else:
        # If not a known/expected type/value (or is a string), treat it as a dimension.
        maybe_description: Optional[str] = None
        if isinstance(col_config, str):
            maybe_description = col_config

        new_dimension = NewQbDimension.from_data(column_name, column_data, description=maybe_description)
        return QbColumn(column_name, new_dimension)


def _get_code_list(column_label: str, maybe_code_list: Optional[Union[bool, str]], column_data: pd.Series):
    if maybe_code_list is not None:
        if isinstance(maybe_code_list, bool):
            code_list = None
        elif isinstance(maybe_code_list, str):
            code_list = ExistingQbCodeList(maybe_code_list)
        else:
            raise Exception(f"Unexpected codelist value '{maybe_code_list}'")
    else:
        code_list = NewQbCodeList.from_data(column_label, column_data)
    return code_list
