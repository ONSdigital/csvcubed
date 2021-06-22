import typing
from typing import Dict, List, Any, Optional, Type, Union, Set
from pathlib import Path
import json
import copy

import pandas as pd

from csvqb.models.cube.cube import Cube, CubeMetadata
from csvqb.models.cube.columns import CsvColumn, SuppressedCsvColumn
from csvqb.models.cube.qb.columns import QbColumn
from csvqb.models.cube.qb.components.component import QbComponent
from csvqb.models.cube.qb.components.observedvalue import QbObservationValue, QbSingleMeasureObservationValue, \
    QbMultiMeasureObservationValue
from csvqb.models.cube.qb.components.dimension import QbMeasureDimension, NewQbDimension, ExistingQbDimension, \
    QbDimension
from csvqb.models.cube.qb.components.measure import ExistingQbMeasure, QbMultiMeasureTypes
from csvqb.models.cube.qb.components.attribute import ExistingQbAttribute, QbUnitAttribute

from csvqb.models.cube.qb.codelist import ExistingQbCodeList, NewQbCodeList, NewQbConcept
from csvqb.utils.dict import get_from_dict_ensure_exists


def get_cube_from_info_json(info_json: Path, cube_id: str, data: pd.DataFrame):
    with open(info_json, "r") as f:
        config = json.load(f)

    config = _override_config_for_cube_id(config, cube_id)
    if config is None:
        raise Exception(f"Config not found for cube with id '{cube_id}'")

    cube = _from_info_json_dict(config, data)
    _validate_csv_qb(cube)
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
    metadata = CubeMetadata(d)
    metadata.dataset_identifier = get_from_dict_ensure_exists(d, "id")
    metadata.base_uri = d.get("baseUri", "http://gss-data.org.uk/")
    columns = _columns_from_info_json(d.get("columns", []), data)

    return Cube(metadata, data, columns)


def _validate_csv_qb(cube: Cube):
    dimension_columns = cube.get_columns_of_type(QbDimension)
    if len(dimension_columns) == 0:
        raise Exception("At least one dimension must be defined.")

    cube.validate()


def _columns_from_info_json(column_mappings: Dict[str, Any], data: pd.DataFrame) -> List[CsvColumn]:
    defined_columns: List[CsvColumn] = []

    for col_title in data.columns:
        column_unique_values: Set[str] = set(data[col_title])
        maybe_config = column_mappings.get(col_title)
        defined_columns.append(_get_column_for_metadata_config(col_title, maybe_config, column_unique_values))

    return defined_columns


def _get_column_for_metadata_config(col_name: str, col_config: Optional[Union[dict, bool]],
                                    column_unique_codes: Set[str]) -> CsvColumn:
    if isinstance(col_config, dict):
        dimension_uri = col_config.get("dimension")
        property_value_url = col_config.get("value")
        parent_uri = col_config.get("parent")
        description = col_config.get("description")
        label = col_config.get("label")
        attribute_uri = col_config.get("attribute")
        unit_uri = col_config.get("unit")
        measure_uri = col_config.get("measure")
        data_type = col_config.get("datatype")

        if dimension_uri is not None and property_value_url is not None:
            if dimension_uri == "http://purl.org/linked-data/cube#measureType":
                # multi-measure cube
                defined_measure_types: List[str] = col_config.get("types", [])
                if len(defined_measure_types) == 0:
                    raise Exception(f"Property 'types' was not defined in measure types column '{col_name}'.")

                measures = QbMultiMeasureTypes([ExistingQbMeasure(t) for t in defined_measure_types])
                return QbColumn(measures, col_name, property_value_url)
            else:
                return QbColumn(ExistingQbDimension(dimension_uri), col_name, property_value_url)
        elif parent_uri is not None or description is not None or label is not None:
            code_list = _get_code_list(col_config.get("codelist"), column_unique_codes)
            new_dimension = NewQbDimension(col_name,
                                           description=description,
                                           parent_dimension_uri=parent_uri,
                                           source_uri=col_config.get("source"),
                                           code_list=code_list)
            return QbColumn(new_dimension, col_name, property_value_url)
        elif attribute_uri is not None and property_value_url is not None:
            return QbColumn(ExistingQbAttribute(attribute_uri), col_name)
        elif unit_uri is not None and measure_uri is not None:
            measure_component = ExistingQbMeasure(measure_uri)
            unit_component = QbUnitAttribute(unit_uri)
            observation_value = QbSingleMeasureObservationValue(measure_component, unit_component, data_type)
            return QbColumn(observation_value, col_name)
        elif data_type is not None:
            return QbColumn(QbMultiMeasureObservationValue(data_type), col_name)
        else:
            raise Exception(f"Unmatched column definition: {col_config}")
    elif isinstance(col_config, bool) and col_config:
        return SuppressedCsvColumn(col_name)
    else:
        # If not a known/expected type/value (or is a string), treat it as a dimension.
        maybe_description: Optional[str] = None
        if isinstance(col_config, str):
            maybe_description = col_config

        new_dimension = NewQbDimension(col_name,
                                       description=maybe_description,
                                       code_list=_get_new_code_list_for_column(column_unique_codes))
        return QbColumn(new_dimension, col_name)


def _get_new_code_list_for_column(unique_column_values: Set[str]):
    new_concepts = {NewQbConcept(c, c) for c in unique_column_values}
    return NewQbCodeList(new_concepts)


def _get_code_list(maybe_code_list: Optional[Union[bool, str]], unique_column_values: Set[str]):
    if maybe_code_list is not None:
        if isinstance(maybe_code_list, bool):
            code_list = None
        elif isinstance(maybe_code_list, str):
            code_list = ExistingQbCodeList(maybe_code_list)
        else:
            raise Exception(f"Unexpected codelist value '{maybe_code_list}'")
    else:
        code_list = _get_new_code_list_for_column(unique_column_values)
    return code_list
