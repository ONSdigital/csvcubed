"""
Models
------

info.json V1.1 column mapping models.
"""
from dataclasses import dataclass, fields, Field, _MISSING_TYPE
from typing import List, Union, Optional, Type, TypeVar
from pathlib import Path

from csvqb.inputs import pandas_input_to_columnar_str
from csvqb.models.cube.qb.components import (
    NewQbDimension,
    ExistingQbDimension,
    NewQbAttribute,
    NewQbAttributeValue,
    ExistingQbAttribute,
    NewQbUnit,
    ExistingQbUnit,
    QbMultiUnits,
    QbMultiMeasureDimension,
    QbMultiMeasureObservationValue,
    QbSingleMeasureObservationValue,
    ExistingQbCodeList,
    ExistingQbMeasure,
    NewQbMeasure,
    QbObservationValue,
    NewQbCodeListInCsvW,
)
from csvqb.inputs import PandasDataTypes
from csvqb.utils.uri import looks_like_uri, csvw_column_name_safe

T = TypeVar("T", bound=object)


def _from_dict(cls: Type[T], d: dict) -> T:
    values = {}
    for field in fields(cls):
        assert isinstance(field, Field)
        if field.name in d.keys():
            values[field.name] = d[field.name]
        elif not isinstance(field.default, _MISSING_TYPE):
            values[field.name] = field.default
        elif not isinstance(field.default_factory, _MISSING_TYPE):
            values[field.name] = field.default_factory()
        else:
            raise ValueError(
                f"Missing required field '{field.name}' on {cls}. Values provided: {d}."
            )
    return cls(**values)  # type: ignore


@dataclass
class NewDimensionProperty:
    codelist: Union[str, bool]
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
    new: Union[NewDimensionProperty, bool]
    value: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "NewDimension":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, dict):
            instance.new = NewDimensionProperty.from_dict(instance.new)  # type: ignore
        return instance

    def map_to_new_qb_dimension(
        self, column_title: str, data: PandasDataTypes, info_json_parent_dir: Path
    ) -> NewQbDimension:
        if isinstance(self.new, bool) and self.new:
            return NewQbDimension.from_data(label=column_title, data=data)
        elif isinstance(self.new, NewDimensionProperty):
            new_dimension = NewQbDimension.from_data(
                label=self.new.label or column_title,
                data=data,
                description=self.new.comment,
                parent_dimension_uri=self.new.subPropertyOf,
                source_uri=self.new.isDefinedBy,
                uri_safe_identifier_override=self.new.path,
            )
            if isinstance(self.new.codelist, str):
                if looks_like_uri(self.new.codelist):
                    new_dimension.code_list = ExistingQbCodeList(self.new.codelist)
                else:
                    code_list_path = Path(self.new.codelist)
                    if code_list_path.is_absolute():
                        new_dimension.code_list = NewQbCodeListInCsvW(code_list_path)
                    else:
                        new_dimension.code_list = NewQbCodeListInCsvW(
                            info_json_parent_dir / self.new.codelist
                        )
            elif isinstance(self.new.codelist, bool):
                if not self.new.codelist:
                    new_dimension.code_list = None
                # else, the user wants a codelist to be automatically generated
            else:
                raise ValueError(f"Unmatched code_list value {self.new.codelist}")
            return new_dimension
        else:
            raise ValueError(f"Unexpected 'new' value: {self.new}")


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
    newAttributeValues: Union[None, bool, List[NewAttributeValue]] = None

    @classmethod
    def from_dict(cls, d: dict) -> "NewAttributeProperty":
        instance = _from_dict(cls, d)
        if isinstance(instance.newAttributeValues, list):
            new_attr_values: List[NewAttributeValue] = [
                NewAttributeValue.from_dict(attr_val)  # type: ignore
                for attr_val in instance.newAttributeValues
            ]
            instance.newAttributeValues = new_attr_values
        return instance


@dataclass
class NewAttribute:
    new: Union[bool, NewAttributeProperty]
    isRequired: bool = False
    value: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "NewAttribute":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, dict):
            instance.new = NewAttributeProperty.from_dict(instance.new)  # type: ignore
        return instance

    def map_to_new_qb_attribute(
        self, column_title: str, data: PandasDataTypes
    ) -> NewQbAttribute:
        if isinstance(self.new, bool) and self.new:
            return NewQbAttribute.from_data(
                label=column_title, data=data, is_required=self.isRequired
            )
        elif isinstance(self.new, NewAttributeProperty):
            return NewQbAttribute(
                label=self.new.label or column_title,
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
    newAttributeValues: Union[None, bool, List[NewAttributeValue]] = None
    isRequired: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "ExistingAttribute":
        instance = _from_dict(cls, d)
        if isinstance(instance.newAttributeValues, list):
            instance.newAttributeValues = [
                NewAttributeValue.from_dict(attr_val)  # type: ignore
                for attr_val in instance.newAttributeValues
            ]
        return instance

    def map_to_existing_qb_attribute(
        self, data: PandasDataTypes
    ) -> ExistingQbAttribute:
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
    new: Union[bool, List[NewResource]]

    @classmethod
    def from_dict(cls, d: dict) -> "NewUnits":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, list):
            instance.new = [
                NewResource.from_dict(attr_val) for attr_val in instance.new  # type: ignore
            ]
        return instance

    def map_to_qb_multi_units(self, data: PandasDataTypes) -> QbMultiUnits:
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
        self, data: PandasDataTypes, column_title: str
    ) -> QbMultiUnits:
        return QbMultiUnits.existing_units_from_data(
            data, csvw_column_name_safe(column_title), self.value
        )


@dataclass
class NewMeasures:
    new: Union[bool, List[NewResource]]

    @classmethod
    def from_dict(cls, d: dict) -> "NewMeasures":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, list):
            instance.new = [
                NewResource.from_dict(attr_val) for attr_val in instance.new  # type: ignore
            ]
        return instance

    def map_to_multi_measure_dimension(
        self, data: PandasDataTypes
    ) -> QbMultiMeasureDimension:
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
    datatype: Optional[str] = None
    unit: Union[None, str, NewResource] = None
    measure: Union[None, str, NewResource] = None

    @classmethod
    def from_dict(cls, d: dict) -> "ObservationValue":
        instance = _from_dict(cls, d)
        if isinstance(instance.unit, dict):
            instance.unit = NewResource.from_dict(instance.unit)  # type: ignore
        if isinstance(instance.measure, dict):
            instance.measure = NewResource.from_dict(instance.measure)  # type: ignore

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
            return QbMultiMeasureObservationValue(
                data_type=self.datatype or "decimal", unit=unit
            )
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
                measure=measure, unit=unit, data_type=self.datatype or "decimal"
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
    new_attribute_values_from_schema: List[NewAttributeValue],
) -> List[NewQbAttributeValue]:
    new_attribute_values = []
    for attr_val in new_attribute_values_from_schema:
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
    new_attribute_values: Union[None, bool, List[NewAttributeValue]],
) -> List[NewQbAttributeValue]:
    if isinstance(new_attribute_values, bool) and new_attribute_values:
        columnar_data = pandas_input_to_columnar_str(data)
        return [NewQbAttributeValue(v) for v in sorted(set(columnar_data))]
    elif isinstance(new_attribute_values, list) and len(new_attribute_values) > 0:
        return _map_attribute_values(new_attribute_values)
    elif new_attribute_values is not None:
        raise ValueError(
            f"Unexpected value for 'newAttributeValues': {new_attribute_values}"
        )

    return []
