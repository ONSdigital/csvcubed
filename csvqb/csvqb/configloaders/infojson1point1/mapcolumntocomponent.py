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
    QbMultiUnits,
    QbMultiMeasureDimension,
    QbMultiMeasureObservationValue,
    QbSingleMeasureObservationValue,
    NewQbCodeList,
    ExistingQbCodeList,
    QbAttribute,
)
from csvqb.inputs import PandasDataTypes


def map_column_to_qb_component(
    column_title: str, column: dict, data: PandasDataTypes
) -> QbColumn:
    """
    Takes an info.json v1.1 column mapping and, if valid,
    returns a :obj:`~csvqb.models.cube.qb.components.datastructuredefinition.QbDataStructureDefinition`.
    """
    schema_model = _from_column_dict_to_model(column)

    if isinstance(schema_model, NewDimension):
        return _map_to_new_dimension(schema_model, data)
    elif isinstance(schema_model, ExistingDimension):
        return QbColumn(
            column_title,
            ExistingQbDimension(schema_model.uri),
            csv_column_uri_template=schema_model.value,
        )
    elif isinstance(schema_model, NewAttribute):
        new_attribute = NewQbAttribute(
            label=schema_model.new.label,
            description=schema_model.new.comment,
            new_attribute_values=_get_new_attribute_values(data, schema_model),
            parent_attribute_uri=schema_model.new.subPropertyOf,
            source_uri=schema_model.new.isDefinedBy,
            is_required=schema_model.isRequired,
            uri_safe_identifier_override=schema_model.new.path,
        )

        return QbColumn(
            column_title,
            new_attribute,
            csv_column_uri_template=schema_model.value,
        )
    elif isinstance(schema_model, ExistingAttribute):
        new_attribute = ExistingQbAttribute(
            schema_model.uri,
            new_attribute_values=_get_new_attribute_values(data, schema_model),
            is_required=schema_model.isRequired,
        )

        return QbColumn(
            column_title,
            new_attribute,
            csv_column_uri_template=schema_model.value,
        )
    if isinstance(schema_model, NewUnits):
        pass
    elif isinstance(schema_model, ExistingUnits):
        pass
    elif isinstance(schema_model, NewMeasures):
        pass
    elif isinstance(schema_model, ExistingMeasures):
        pass
    elif isinstance(schema_model, ObservationValue):
        pass
    else:
        raise ValueError(f"Unmatched schema model type {type(schema_model)}")


def _get_new_attribute_values(
    data: PandasDataTypes, schema_model: Union[ExistingAttribute, NewAttribute]
) -> Optional[List[NewQbAttributeValue]]:
    if (
        isinstance(schema_model.newAttributeValues, bool)
        and schema_model.newAttributeValues
    ):
        columnar_data = pandas_input_to_columnar_str(data)
        return [NewQbAttributeValue(v) for v in sorted(set(columnar_data))]
    elif (
        isinstance(schema_model.newAttributeValues, list)
        and len(schema_model.newAttributeValues) > 0
    ):
        return _map_attribute_values(schema_model)
    elif schema_model.newAttributeValues is not None:
        raise ValueError(
            f"Unexpected value for 'newAttributeValues': {schema_model.newAttributeValues}"
        )

    return None


def _map_attribute_values(
    schema_model: Union[ExistingAttribute, NewAttribute]
) -> List[NewQbAttributeValue]:
    new_attribute_values = []
    for attr_val in schema_model.newAttributeValues:
        if not isinstance(attr_val, NewAttributeValue):
            raise ValueError(f"Found unexpected attribute value {attr_val}")

        new_attribute_values.append(
            NewQbAttributeValue(
                label=attr_val.label,
                description=attr_val.comment,
                source_uri=attr_val.isDefinedBy,
                uri_safe_identifier_override=attr_val.path,
            )
        )
    return new_attribute_values


def _map_to_new_dimension(
    column_title: str, dim: NewDimension, data: PandasDataTypes
) -> QbColumn[NewQbDimension]:
    new_dimension = NewQbDimension.from_data(
        label=dim.new.label,
        data=data,
        description=dim.new.comment,
        parent_dimension_uri=dim.new.subPropertyOf,
        source_uri=dim.new.isDefinedBy,
        uri_safe_identifier_override=dim.new.path,
    )
    codelist = False
    if isinstance(new.codelist, str):
        if looks_like_uri(new.codelist):
            new_dimension.code_list = ExistingQbCodeList(new.codelist)
        else:
            # todo: Need a new type to represent an existing CSV-W codelist file.
            pass
    elif isinstance(new.codelist, bool):
        if not new.codelist:
            new_dimension.code_list = None
    else:
        raise ValueError(f"Unmatched code_list value {new.codelist}")
    return QbColumn(column_title, new_dimension, csv_column_uri_template=dim.value)


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
