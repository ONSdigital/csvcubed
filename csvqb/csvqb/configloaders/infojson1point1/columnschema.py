"""
Models
------

info.json V1.1 column mapping models.
"""
from dataclasses import dataclass, fields, Field
from typing import Any, List, Union, Optional, Type, TypeVar

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
    QbObservationValue,
)
from csvqb.inputs import PandasDataTypes
from csvqb.utils.uri import looks_like_uri, csvw_column_name_safe

T = TypeVar("T", bound=object)


def _from_dict(cls: Type[T], d: dict) -> T:
    instance = cls()
    for field in fields(instance):
        assert isinstance(field, Field)
        if field.name in d.keys():
            setattr(instance, field.name, d[field.name])


@dataclass
class NewDimensionProperty:
    codelist: Union[str, False]
    path: Optional[str] = None
    label: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None
    subPropertyOf: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "NewDimensionProperty":
        return _from_dict(cls, d)


@dataclass
class NewDimension:
    new: Union[NewDimensionProperty, True]
    value: Optional[str]

    @classmethod
    def from_dict(cls, d: dict) -> "NewDimensionProperty":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, dict):
            instance.new = NewDimensionProperty.from_dict(instance.new)
        return instance

    def map_to_new_qb_dimension(self) -> NewQbDimension:
        new_dimension = NewQbDimension.from_data(
            label=self.new.label,
            data=data,
            description=self.new.comment,
            parent_dimension_uri=self.new.subPropertyOf,
            source_uri=self.new.isDefinedBy,
            uri_safe_identifier_override=self.new.path,
        )
        codelist = False
        if isinstance(self.new.codelist, str):
            if looks_like_uri(self.new.codelist):
                new_dimension.code_list = ExistingQbCodeList(self.new.codelist)
            else:
                # todo: Need a new type to represent an existing CSV-W codelist file.
                pass
        elif isinstance(self.new.codelist, bool):
            if not self.new.codelist:
                new_dimension.code_list = None
        else:
            raise ValueError(f"Unmatched code_list value {new.codelist}")

        return new_dimension


@dataclass
class ExistingDimension:
    uri: str
    value: str

    @classmethod
    def from_dict(cls, d: dict) -> "ExistingDimension":
        return _from_dict(cls, d)

    def map_to_existing_qb_dimension(self) -> ExistingQbDimension:
        return ExistingQbDimension(self.uri)


@dataclass
class NewAttributeValue:
    label: str
    path: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "NewAttributeValue":
        return _from_dict(cls, d)


@dataclass
class NewAttributeProperty:
    path: Optional[str] = None
    label: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None
    subPropertyOf: Optional[str] = None
    newAttributeValues: Union[None, True, List[NewAttributeValue]] = None

    @classmethod
    def from_dict(cls, d: dict) -> "ExistingDimension":
        instance = _from_dict(cls, d)
        if isinstance(instance.newAttributeValues, list):
            instance.newAttributeValues = [
                NewDimensionProperty.from_dict(attr_val)
                for attr_val in instance.newAttributeValues
            ]
        return instance


@dataclass
class NewAttribute:
    new: Union[True, NewAttributeProperty]
    isRequired: Optional[bool] = True

    @classmethod
    def from_dict(cls, d: dict) -> "NewAttribute":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, dict):
            instance.new = NewAttributeProperty.from_dict(instance.new)
        return instance

    def map_to_new_qb_attribute(self) -> NewQbAttribute:
        if isinstance(self.new, bool) and self.new:
            return NewQbAttribute.from_data(label=column_title, data=data)
        elif isinstance(self.new, NewAttributeProperty):
            return NewQbAttribute(
                label=self.new.label,
                description=self.new.comment,
                new_attribute_values=_get_new_attribute_values(
                    data, self.new.newAttributeValues
                ),
                parent_attribute_uri=self.new.subPropertyOf,
                source_uri=self.new.isDefinedBy,
                is_required=self.isRequired,
                uri_safe_identifier_override=self.new.path,
            )
        else:
            raise ValueError(f"Unhandled 'new' value: {self.new}")


@dataclass
class ExistingAttribute:
    uri: str
    value: Optional[str] = None
    newAttributeValues: Union[None, True, List[NewAttributeValue]] = None
    isRequired: Optional[bool] = True

    @classmethod
    def from_dict(cls, d: dict) -> "ExistingAttribute":
        instance = _from_dict(cls, d)
        if isinstance(instance.newAttributeValues, list):
            instance.newAttributeValues = [
                NewAttributeValue.from_dict(attr_val)
                for attr_val in instance.newAttributeValues
            ]
        return instance

    def map_to_existing_qb_attribute(self) -> ExistingQbAttribute:
        return ExistingQbAttribute(
            self.uri,
            new_attribute_values=_get_new_attribute_values(
                data, self.newAttributeValues
            ),
            is_required=self.isRequired,
        )


@dataclass
class NewResource:
    label: str
    path: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "NewResource":
        return _from_dict(cls, d)


@dataclass
class NewUnits:
    new: Union[True, List[NewResource]]

    @classmethod
    def from_dict(cls, d: dict) -> "NewUnits":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, list):
            instance.new = [
                NewResource.from_dict(attr_val) for attr_val in instance.new
            ]
        return instance

    def map_to_qb_multi_units(self) -> QbMultiUnits:
        if isinstance(self.new, bool) and self.new:
            return QbMultiUnits.new_units_from_data(data)
        elif isinstance(self.new, list):
            units = []
            for unit in self.new:
                if not isinstance(unit, NewResource):
                    raise ValueError(f"Unexpected unit value: {unit}")
                units.append(_map_new_resource_to_unit(unit))

            return QbMultiUnits(units)
        else:
            raise ValueError(f"Unhandled 'new' value: {self.new}")


@dataclass
class ExistingUnits:
    value: str

    @classmethod
    def from_dict(cls, d: dict) -> "ExistingUnits":
        return _from_dict(cls, d)

    def map_to_qb_multi_units(
        self, data: PandasDataTypes, column_title: str, csv_column_uri_template: str
    ) -> QbMultiUnits:
        return QbMultiUnits.existing_units_from_data(
            data, csvw_column_name_safe(column_title), csv_column_uri_template
        )


@dataclass
class NewMeasures:
    new: Union[True, List[NewResource]]

    @classmethod
    def from_dict(cls, d: dict) -> "NewMeasures":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, list):
            instance.new = [
                NewResource.from_dict(attr_val) for attr_val in instance.new
            ]
        return instance

    def map_to_multi_measure_dimension(self) -> QbMultiMeasureDimension:
        if isinstance(self.new, bool) and self.new:
            return QbMultiMeasureDimension.new_measures_from_data(data)
        elif isinstance(self.new, list):
            new_measures = []
            for new_measure in self.new:
                if not isinstance(new_measure, NewResource):
                    raise ValueError(f"Unexpected measure: {new_measure}")
                new_measures.append(_map_new_resource_to_measure(new_measure))
            return QbMultiMeasureDimension(new_measures)
        else:
            raise ValueError(f"Unexpected 'new' value: {self.new}")


@dataclass
class ExistingMeasures:
    value: str

    @classmethod
    def from_dict(cls, d: dict) -> "ExistingMeasures":
        return _from_dict(cls, d)

    def map_to_multi_measure_dimension(
        self, column_title: str, data: PandasDataTypes
    ) -> QbMultiMeasureDimension:
        csvw_column_name = csvw_column_name_safe(column_title)
        return QbMultiMeasureDimension.existing_measures_from_data(
            data, csvw_column_name, self.value
        )


@dataclass
class ObservationValue:
    datatype: Optional[str]
    unit: Union[None, str, NewResource] = None
    measure: Union[None, str, NewResource] = None

    @classmethod
    def from_dict(cls, d: dict) -> "ObservationValue":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, dict):
            instance.unit = NewResource.from_dict(instance.unit)
        if isinstance(instance.measure, dict):
            instance.measure = NewResource.from_dict(instance.measure)

        return instance

    def map_to_qb_observation(self) -> QbObservationValue:
        unit = None
        if isinstance(self.unit, str):
            unit = ExistingQbUnit(unit_uri=self.unit)
        elif isinstance(self.unit, NewResource):
            unit = _map_new_resource_to_unit(self.unit)
        elif self.unit is not None:
            raise ValueError(f"Unexpected unit: {self.unit}")

        if self.measure is None:
            # Multi-measure cube
            return QbMultiMeasureObservationValue(data_type=self.datatype, unit=unit)
        else:
            # Single measure qb
            measure = None
            if isinstance(self.measure, str):
                measure = ExistingQbMeasure(self.measure)
            elif isinstance(self.measure, NewResource):
                measure = _map_new_resource_to_measure(self.measure)
            else:
                raise ValueError(f"Unhandled measure type: {self.measure}")

            return QbSingleMeasureObservationValue(
                measure=measure, unit=unit, data_type=self.datatype
            )


def _map_new_resource_to_unit(resource: NewResource) -> NewQbUnit:
    return NewQbUnit(
        label=resource.label,
        description=resource.comment,
        source_uri=resource.isDefinedBy,
        uri_safe_identifier_override=resource.path,
    )


def _map_new_resource_to_measure(resource: NewResource) -> NewQbMeasure:
    return NewQbMeasure(
        label=resource.label,
        description=resource.comment,
        source_uri=resource.isDefinedBy,
        uri_safe_identifier_override=resource.path,
    )


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


def _get_new_attribute_values(
    data: PandasDataTypes,
    newAttributeValues: Union[None, True, List[NewAttributeValue]],
) -> Optional[List[NewQbAttributeValue]]:
    if isinstance(newAttributeValues, bool) and newAttributeValues:
        columnar_data = pandas_input_to_columnar_str(data)
        return [NewQbAttributeValue(v) for v in sorted(set(columnar_data))]
    elif isinstance(newAttributeValues, list) and len(newAttributeValues) > 0:
        return _map_attribute_values(newAttributeValues)
    elif newAttributeValues is not None:
        raise ValueError(
            f"Unexpected value for 'newAttributeValues': {newAttributeValues}"
        )

    return None
