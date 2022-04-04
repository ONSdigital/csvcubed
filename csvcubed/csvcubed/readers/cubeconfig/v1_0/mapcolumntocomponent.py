"""
Mapping
-------

Map info.json V1.1 definitions to QB column components
"""
import copy
from typing import Union

from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.inputs import PandasDataTypes

import csvcubed.readers.cubeconfig.v1_0.columnschema as schema


def map_column_to_qb_component(
    column_title: str, column: dict, data: PandasDataTypes
) -> QbColumn:
    """
    Takes a config.json v1.0 column mapping and, if valid,
    returns a :obj:`~csvcubed.models.cube.qb.columns.QbColumn`.
    """
    schema_mapping = _from_column_dict_to_schema_model(column_title, column)

    if isinstance(schema_mapping, schema.NewDimension):
        return QbColumn(
            column_title,
            schema_mapping.map_to_new_qb_dimension(column_title, data),
            csv_column_uri_template=schema_mapping.cell_uri_template,
        )

    elif isinstance(schema_mapping, schema.ExistingDimension):
        return QbColumn(
            column_title,
            schema_mapping.map_to_existing_qb_dimension(),
            csv_column_uri_template=schema_mapping.cell_uri_template,
        )

    elif isinstance(schema_mapping, schema.NewAttribute):
        return QbColumn(
            column_title,
            schema_mapping.map_to_new_qb_attribute(column_title, data),
            csv_column_uri_template=schema_mapping.cell_uri_template,
        )

    elif isinstance(schema_mapping, schema.ExistingAttribute):
        return QbColumn(
            column_title,
            schema_mapping.map_to_existing_qb_attribute(data),
            csv_column_uri_template=schema_mapping.cell_uri_template,
        )

    elif isinstance(schema_mapping, schema.NewUnits):
        return QbColumn(column_title, schema_mapping.map_to_new_qb_multi_units(data))

    elif isinstance(schema_mapping, schema.ExistingUnits):
        return QbColumn(
            column_title,
            schema_mapping.map_to_existing_qb_multi_units(data, column_title),
            csv_column_uri_template=schema_mapping.cell_uri_template,
        )

    elif isinstance(schema_mapping, schema.NewMeasures):
        return QbColumn(
            column_title, schema_mapping.map_to_new_multi_measure_dimension(data)
        )

    elif isinstance(schema_mapping, schema.ExistingMeasures):
        return QbColumn(
            column_title,
            schema_mapping.map_to_existing_multi_measure_dimension(column_title, data),
            csv_column_uri_template=schema_mapping.cell_uri_template,
        )

    elif isinstance(schema_mapping, schema.ObservationValue):
        return QbColumn(column_title, schema_mapping.map_to_qb_observation())

    else:
        raise ValueError(f"Unmatched column type {type(schema_mapping)}")


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
    N.B. when using the :meth:`dict_fields_match_class` method, we need to ensure that we check for types with
    required properties *before* types without required properties.
    """
    column_type = column.get("type", "dimension")
    column_without_type = copy.deepcopy(column)
    if "type" in column_without_type:
        del column_without_type["type"]

    if column_type == "dimension":
        if schema.ExistingDimension.dict_fields_match_class(column_without_type):
            return schema.ExistingDimension.from_dict(column_without_type)
        elif schema.NewDimension.dict_fields_match_class(column_without_type):
            return schema.NewDimension.from_dict(column_without_type)
        else:
            raise Exception(
                f"Column with config: '{column}' did not match "
                f"either New or Existing Dimension using schema"
            )
    elif column_type == "attribute":
        if schema.NewAttribute.dict_fields_match_class(column_without_type):
            if schema.ExistingAttribute.dict_fields_match_class(column_without_type):
                return schema.ExistingAttribute.from_dict(column_without_type)
            else:
                return schema.NewAttribute.from_dict(column_without_type)
        elif schema.ExistingAttribute.dict_fields_match_class(column_without_type):
            return schema.ExistingAttribute.from_dict(column_without_type)
        else:
            raise Exception(
                f"Column with config '{column}' did not match either New or "
                f"Existing Attribute schema"
            )
    elif column_type == "units":
        if schema.ExistingUnits.dict_fields_match_class(column_without_type):
            return schema.ExistingUnits.from_dict(column_without_type)
        elif schema.NewUnits.dict_fields_match_class(column_without_type):
            return schema.NewUnits.from_dict(column_without_type)
        else:
            raise Exception(
                f"Column with type '{column_type}' did not match either New or "
                f"Existing Units schema"
            )
    elif column_type == "measures":
        if schema.ExistingMeasures.dict_fields_match_class(column_without_type):
            return schema.ExistingMeasures.from_dict(column_without_type)
        elif schema.NewMeasures.dict_fields_match_class(column_without_type):
            return schema.NewMeasures.from_dict(column_without_type)
        else:
            raise Exception(
                f"Column with type '{column_type}' did not match either New or "
                f"Existing Measures schema"
            )
    elif column_type == "observations":
        return schema.ObservationValue.from_dict(column)

    raise ValueError(
        f"Column '{column_title}' with type '{column_type}' could not be understood."
    )
