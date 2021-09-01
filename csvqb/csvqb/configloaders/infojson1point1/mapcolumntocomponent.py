"""
Mapping
-------

Map info.json V1.1 definitions to QB column components
"""
from .columnschema import (
    NewDimension,
    ExistingDimension,
    NewAttribute,
    ExistingAttribute,
    NewUnits,
    ExistingUnits,
    NewMeasures,
    ExistingMeasures,
    ObservationValue,
    NewAttributeValue,
    NewAttributeProperty,
    NewResource,
)
from csvqb.models.cube.qb.components.datastructuredefinition import (
    QbDataStructureDefinition,
)
from csvqb.models.cube.qb.columns import QbColumn
from csvqb.models.cube.qb.components import (
    NewQbDimension,
    ExistingQbDimension,
    NewQbAttribute,
    NewQbAttributeValue,
    ExistingQbAttribute,
    NewQbUnit,
    ExistingQbUnit,
    QbUnit,
    QbMultiUnits,
    QbMultiMeasureDimension,
    QbMultiMeasureObservationValue,
    QbSingleMeasureObservationValue,
    NewQbCodeList,
    ExistingQbCodeList,
    QbAttribute,
    QbMeasure,
    ExistingQbMeasure,
    NewQbMeasure,
)
from csvqb.inputs import PandasDataTypes
from csvqb.utils.uri import looks_like_uri, csvw_column_name_safe


def map_column_to_qb_component(
    column_title: str, column: dict, data: PandasDataTypes
) -> QbColumn:
    """
    Takes an info.json v1.1 column mapping and, if valid,
    returns a :obj:`~csvqb.models.cube.qb.components.datastructuredefinition.QbDataStructureDefinition`.
    """
    schema_mapping = _from_column_dict_to_model(column)

    if isinstance(schema_mapping, NewDimension):
        return QbColumn(
            column_title,
            schema_mapping.map_to_new_qb_dimension(),
            csv_column_uri_template=schema_mapping.value,
        )
    elif isinstance(schema_mapping, ExistingDimension):
        return QbColumn(
            column_title,
            schema_mapping.map_to_existing_qb_dimension(),
            csv_column_uri_template=schema_mapping.value,
        )
    elif isinstance(schema_mapping, NewAttribute):
        return QbColumn(
            column_title,
            schema_mapping.map_to_new_qb_attribute(),
            csv_column_uri_template=schema_mapping.value,
        )
    elif isinstance(schema_mapping, ExistingAttribute):
        return QbColumn(
            column_title,
            schema_mapping.map_to_existing_qb_attribute(),
            csv_column_uri_template=schema_mapping.value,
        )
    if isinstance(schema_mapping, NewUnits):
        return QbColumn(column_title, schema_mapping.map_to_qb_multi_units())
    elif isinstance(schema_mapping, ExistingUnits):
        return QbColumn(
            column_title,
            schema_mapping.map_to_qb_multi_units(column_title, schema_mapping.value),
            schema_mapping.value,
        )
    elif isinstance(schema_mapping, NewMeasures):
        return QbColumn(column_title, schema_mapping.map_to_multi_measure_dimension())
    elif isinstance(schema_mapping, ExistingMeasures):
        return QbColumn(
            column_title,
            schema_mapping.map_to_multi_measure_dimension(column_title, data),
            schema_mapping.value,
        )
    elif isinstance(schema_mapping, ObservationValue):
        return QbColumn(column_title, schema_mapping.map_to_qb_observation())
    else:
        raise ValueError(f"Unmatched schema model type {type(schema_mapping)}")


def _from_column_dict_to_model(
    column: dict,
) -> Union[
    NewDimension,
    ExistingDimension,
    NewAttribute,
    ExistingAttribute,
    NewUnits,
    ExistingUnits,
    NewMeasures,
    ExistingMeasures,
    ObservationValue,
]:
    column_type = column.get("type")
    new_value = column.get("new")
    if column_type is None:
        raise ValueError("Type of column not specified.")
    elif column_type == "dimension":
        if new_value is not None:
            return NewDimension.from_dict(column)
        else:
            return ExistingDimension.from_dict(column)
    elif column_type == "attribute":
        if new_value is not None:
            return NewAttribute.from_dict(column)
        else:
            return ExistingAttribute.from_dict(column)
    elif column_type == "units":
        if new_value is not None:
            return NewUnits.from_dict(column)
        else:
            return ExistingUnits.from_dict(column)
    elif column_type == "measure":
        if new_value is not None:
            return NewMeasures.from_dict(column)
        else:
            return ExistingMeasures.from_dict(column)
    elif column_type == "observation":
        return ObservationValue.from_dict(column)
    else:
        raise ValueError(f"Type of column '{column_type}' not handled.")
