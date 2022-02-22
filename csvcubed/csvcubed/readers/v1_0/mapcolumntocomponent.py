"""
Mapping
-------

Map info.json V1.1 definitions to QB column components
"""
import copy
from typing import Union
from pathlib import Path

from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.inputs import PandasDataTypes

from csvcubed.readers.v1_0 import columnschema as schema


def map_column_to_qb_component(
        column_title: str,
        column: dict,
        data: PandasDataTypes,
        json_parent_dir: Path
) -> QbColumn:
    """
    Takes an config.json v1.0 column mapping and, if valid,
    returns a :obj:`~csvcubed.models.cube.qb.components.datastructuredefinition.QbDataStructureDefinition`.
    """
    schema_mapping = _from_column_dict_to_schema_model(column_title, column)

    if isinstance(schema_mapping, schema.Dimension):
        return QbColumn(
            column_title,
            schema_mapping.map_to_qb_dimension(column_title, data, json_parent_dir),
            csv_column_uri_template=schema_mapping.cell_uri_template
        )

    elif isinstance(schema_mapping, schema.Attribute):
        return QbColumn(
            column_title,
            schema_mapping.map_to_qb_attribute(column_title, data)
        )

    elif isinstance(schema_mapping, schema.Units):
        return QbColumn(
            column_title,
            schema_mapping.map_to_qb_multi_units(data))

    elif isinstance(schema_mapping, schema.Measures):
        return QbColumn(
            column_title,
            schema_mapping.map_to_multi_measure_dimension(data)
        )

    elif isinstance(schema_mapping, schema.ObservationValue):
        return QbColumn(
            column_title,
            schema_mapping.map_to_qb_observation())

    else:
        raise ValueError(f"Unmatched schema model type {type(schema_mapping)}")


def _from_column_dict_to_schema_model(
    column_title: str,
    column: dict,
) -> Union[
    schema.Dimension,
    schema.Attribute,
    schema.Units,
    schema.Measures,
    schema.ObservationValue,
]:
    """
    N.B. when using the :method:`dict_fields_match_class` method, we need to ensure that we check for types with
    required properties *before* types without required properties.
    """
    column_type = column.get("type")
    column_without_type = copy.deepcopy(column)
    del column_without_type["type"]

    if column_type is None:
        raise ValueError("Type of column not specified.")
    elif column_type == "dimension":
        if schema.Dimension.dict_fields_match_class(column_without_type):
            return schema.Dimension.from_dict(column)

    elif column_type == "attribute":
        if schema.Attribute.dict_fields_match_class(column_without_type):
            return schema.Attribute.from_dict(column)

    elif column_type == "units":
        if schema.Units.dict_fields_match_class(column_without_type):
            return schema.Units.from_dict(column)

    elif column_type == "measures":
        if schema.Measures.dict_fields_match_class(column_without_type):
            return schema.Measures.from_dict(column)

    elif column_type == "observations":
        return schema.ObservationValue.from_dict(column)

    raise ValueError(
        f"Column '{column_title}' with type '{column_type}' could not be understood."
    )
