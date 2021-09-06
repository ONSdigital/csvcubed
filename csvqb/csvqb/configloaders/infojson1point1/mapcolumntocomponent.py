"""
Mapping
-------

Map info.json V1.1 definitions to QB column components
"""
from typing import Union
from pathlib import Path

import csvqb.configloaders.infojson1point1.columnschema as schema
from csvqb.models.cube.qb.columns import QbColumn
from csvqb.inputs import PandasDataTypes


def map_column_to_qb_component(
    column_title: str, column: dict, data: PandasDataTypes, info_json_parent_dir: Path
) -> QbColumn:
    """
    Takes an info.json v1.1 column mapping and, if valid,
    returns a :obj:`~csvqb.models.cube.qb.components.datastructuredefinition.QbDataStructureDefinition`.
    """
    schema_mapping = _from_column_dict_to_schema_model(column_title, column)

    if isinstance(schema_mapping, schema.NewDimension):
        return QbColumn(
            column_title,
            schema_mapping.map_to_new_qb_dimension(
                column_title, data, info_json_parent_dir
            ),
            csv_column_uri_template=schema_mapping.value,
        )
    elif isinstance(schema_mapping, schema.ExistingDimension):
        return QbColumn(
            column_title,
            schema_mapping.map_to_existing_qb_dimension(),
            csv_column_uri_template=schema_mapping.value,
        )
    elif isinstance(schema_mapping, schema.NewAttribute):
        return QbColumn(
            column_title,
            schema_mapping.map_to_new_qb_attribute(column_title, data),
            csv_column_uri_template=schema_mapping.value,
        )
    elif isinstance(schema_mapping, schema.ExistingAttribute):
        return QbColumn(
            column_title,
            schema_mapping.map_to_existing_qb_attribute(data),
            csv_column_uri_template=schema_mapping.value,
        )
    if isinstance(schema_mapping, schema.NewUnits):
        return QbColumn(column_title, schema_mapping.map_to_qb_multi_units(data))
    elif isinstance(schema_mapping, schema.ExistingUnits):
        return QbColumn(
            column_title,
            schema_mapping.map_to_qb_multi_units(data, column_title),
            csv_column_uri_template=schema_mapping.value,
        )
    elif isinstance(schema_mapping, schema.NewMeasures):
        return QbColumn(
            column_title, schema_mapping.map_to_multi_measure_dimension(data)
        )
    elif isinstance(schema_mapping, schema.ExistingMeasures):
        return QbColumn(
            column_title,
            schema_mapping.map_to_multi_measure_dimension(column_title, data),
            csv_column_uri_template=schema_mapping.value,
        )
    elif isinstance(schema_mapping, schema.ObservationValue):
        return QbColumn(column_title, schema_mapping.map_to_qb_observation())
    else:
        raise ValueError(f"Unmatched schema model type {type(schema_mapping)}")


def _from_column_dict_to_schema_model(
    column_title: str,
    column: dict,
) -> Union[
    schema.NewDimension,
    schema.ExistingDimension,
    schema.NewAttribute,
    schema.ExistingAttribute,
    schema.NewUnits,
    schema.ExistingUnits,
    schema.NewMeasures,
    schema.ExistingMeasures,
    schema.ObservationValue,
]:
    """
    N.B. when using the :method:`dict_has_required_fields` method, we need to ensure that we check for types with
    required properties *before* types without required properties.
    """
    column_type = column.get("type")
    if column_type is None:
        raise ValueError("Type of column not specified.")
    elif column_type == "dimension":
        if schema.ExistingDimension.dict_has_required_fields(column):
            return schema.ExistingDimension.from_dict(column)
        elif schema.NewDimension.dict_has_required_fields(column):
            return schema.NewDimension.from_dict(column)
    elif column_type == "attribute":
        if schema.ExistingAttribute.dict_has_required_fields(column):
            return schema.ExistingAttribute.from_dict(column)
        elif schema.NewAttribute.dict_has_required_fields(column):
            return schema.NewAttribute.from_dict(column)
    elif column_type == "units":
        if schema.ExistingUnits.dict_has_required_fields(column):
            return schema.ExistingUnits.from_dict(column)
        elif schema.NewUnits.dict_has_required_fields(column):
            return schema.NewUnits.from_dict(column)
    elif column_type == "measures":
        if schema.ExistingMeasures.dict_has_required_fields(column):
            return schema.ExistingMeasures.from_dict(column)
        elif schema.NewMeasures.dict_has_required_fields(column):
            return schema.NewMeasures.from_dict(column)
    elif column_type == "observations":
        return schema.ObservationValue.from_dict(column)
    else:
        raise ValueError(
            f"Column '{column_title}' with type '{column_type}' could not be understood."
        )
