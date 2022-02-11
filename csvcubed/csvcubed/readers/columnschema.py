"""
Models
------

info.json V1.1 column mapping models.
"""
from dataclasses import dataclass
from typing import List, Union, Optional, TypeVar
from pathlib import Path

import uritemplate
from csvcubed.models.cube import (
    ExistingQbAttributeLiteral,
    NewQbAttributeLiteral,
    CompositeQbCodeList,
    CatalogMetadata,
    DuplicatedQbConcept,
    NewQbCodeList,
)
from csvcubedmodels.dataclassbase import DataClassBase

from csvcubed.inputs import pandas_input_to_columnar_optional_str
from csvcubed.models.cube.qb.components import (
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
from csvcubed.inputs import PandasDataTypes
from csvcubed.utils.uri import looks_like_uri, csvw_column_name_safe

T = TypeVar("T", bound=object)


@dataclass
class SchemaBaseClass(DataClassBase):
    ...


@dataclass
class NewDimensionProperty(SchemaBaseClass):
    codelist: Union[str, bool]
    path: Optional[str] = None
    label: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None
    subPropertyOf: Optional[str] = None


@dataclass
class NewDimension(SchemaBaseClass):
    new: Union[NewDimensionProperty, bool] = True
    value: Optional[str] = None

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
                elif (
                    self.new.subPropertyOf
                    == "http://purl.org/linked-data/sdmx/2009/dimension#refPeriod"
                    and self.value is not None
                    and self.value.lower().startswith(
                        "http://reference.data.gov.uk/id/"
                    )
                ):
                    # This is a special case where we build up a code-list of the date/time values.
                    new_dimension.code_list = (
                        self._get_date_time_code_list_for_dimension(
                            column_title, new_dimension
                        )
                    )
                # else, the user wants a standard codelist to be automatically generated
            else:
                raise ValueError(f"Unmatched code_list value {self.new.codelist}")
            return new_dimension
        else:
            raise ValueError(f"Unexpected 'new' value: {self.new}")

    def _get_date_time_code_list_for_dimension(
        self, column_title: str, new_dimension: NewQbDimension
    ) -> CompositeQbCodeList:
        csvw_safe_column_title = csvw_column_name_safe(column_title)
        assert isinstance(new_dimension.code_list, NewQbCodeList)
        return CompositeQbCodeList(
            CatalogMetadata(new_dimension.label),
            [
                DuplicatedQbConcept(
                    existing_concept_uri=uritemplate.expand(
                        self.value,
                        {csvw_safe_column_title: c.label},
                    ),
                    label=c.label,
                    code=c.code,
                )
                for c in new_dimension.code_list.concepts
            ],
        )


@dataclass
class ExistingDimension(SchemaBaseClass):
    uri: str
    value: str

    def map_to_existing_qb_dimension(self) -> ExistingQbDimension:
        return ExistingQbDimension(self.uri)


@dataclass
class NewAttributeValue(SchemaBaseClass):
    label: str
    path: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None


@dataclass
class NewAttributeProperty(SchemaBaseClass):
    path: Optional[str] = None
    label: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None
    subPropertyOf: Optional[str] = None
    newAttributeValues: Union[None, bool, List[NewAttributeValue]] = None
    literalValuesDataType: Optional[str] = None


@dataclass
class NewAttribute(SchemaBaseClass):
    new: Union[bool, NewAttributeProperty] = True
    isRequired: bool = False
    value: Optional[str] = None

    def map_to_new_qb_attribute(
        self, column_title: str, data: PandasDataTypes
    ) -> NewQbAttribute:
        if (
            isinstance(self.new, NewAttributeProperty)
            and self.new.literalValuesDataType is not None
        ):
            if self.new.newAttributeValues:
                raise Exception(
                    "Attributes cannot represent both literal values and attribute (resource) values"
                )
            return NewQbAttributeLiteral(
                label=self.new.label or column_title,
                description=self.new.comment,
                data_type=self.new.literalValuesDataType,
                parent_attribute_uri=self.new.subPropertyOf,
                source_uri=self.new.isDefinedBy,
                is_required=self.isRequired,
                uri_safe_identifier_override=self.new.path,
            )
        else:
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
class ExistingAttribute(SchemaBaseClass):
    uri: str
    value: Optional[str] = None
    newAttributeValues: Union[None, bool, List[NewAttributeValue]] = None
    isRequired: bool = False
    literalValuesDataType: Optional[str] = None

    def map_to_existing_qb_attribute(
        self, data: PandasDataTypes
    ) -> Union[ExistingQbAttribute, ExistingQbAttributeLiteral]:
        if self.literalValuesDataType is None:
            return ExistingQbAttribute(
                self.uri,
                new_attribute_values=_get_new_attribute_values(
                    data, self.newAttributeValues
                ),
                is_required=self.isRequired,
            )
        else:
            if self.newAttributeValues:
                raise Exception(
                    "Attributes cannot represent both literal values and attribute (resource) values"
                )
            return ExistingQbAttributeLiteral(
                attribute_uri=self.uri,
                data_type=self.literalValuesDataType,
                is_required=self.isRequired,
            )


@dataclass
class NewMeasure(SchemaBaseClass):
    label: str
    path: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None


@dataclass
class NewUnit(SchemaBaseClass):
    label: str
    path: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None
    baseUnit: Optional[str] = None
    baseUnitScalingFactor: Optional[float] = None
    qudtQuantityKind: Optional[str] = None
    siBaseUnitConversionMultiplier: Optional[float] = None


@dataclass
class NewUnits(SchemaBaseClass):
    new: Union[bool, List[NewUnit]] = True

    def map_to_qb_multi_units(self, data: PandasDataTypes) -> QbMultiUnits:
        if isinstance(self.new, bool) and self.new:
            return QbMultiUnits.new_units_from_data(data)
        elif isinstance(self.new, list):
            units = []
            for unit in self.new:
                if not isinstance(unit, NewUnit):
                    raise ValueError(f"Unexpected unit value: {unit}")
                units.append(_map_unit(unit))

            return QbMultiUnits(units)
        else:
            raise ValueError(f"Unhandled 'new' value: {self.new}")


@dataclass
class ExistingUnits(SchemaBaseClass):
    value: str

    def map_to_qb_multi_units(
        self, data: PandasDataTypes, column_title: str
    ) -> QbMultiUnits:
        return QbMultiUnits.existing_units_from_data(
            data, csvw_column_name_safe(column_title), self.value
        )


@dataclass
class NewMeasures(SchemaBaseClass):
    new: Union[bool, List[NewMeasure]] = True

    def map_to_multi_measure_dimension(
        self, data: PandasDataTypes
    ) -> QbMultiMeasureDimension:
        if isinstance(self.new, bool) and self.new:
            return QbMultiMeasureDimension.new_measures_from_data(data)
        elif isinstance(self.new, list):
            new_measures = []
            for new_measure in self.new:
                if not isinstance(new_measure, NewMeasure):
                    raise ValueError(f"Unexpected measure: {new_measure}")
                new_measures.append(_map_measure(new_measure))
            return QbMultiMeasureDimension(new_measures)
        else:
            raise ValueError(f"Unexpected 'new' value: {self.new}")


@dataclass
class ExistingMeasures(SchemaBaseClass):
    value: str

    def map_to_multi_measure_dimension(
        self, column_title: str, data: PandasDataTypes
    ) -> QbMultiMeasureDimension:
        csvw_column_name = csvw_column_name_safe(column_title)
        return QbMultiMeasureDimension.existing_measures_from_data(
            data, csvw_column_name, self.value
        )


@dataclass
class ObservationValue(SchemaBaseClass):
    datatype: Optional[str] = None
    unit: Union[None, str, NewUnit] = None
    measure: Union[None, str, NewMeasure] = None

    def map_to_qb_observation(self) -> QbObservationValue:
        unit = None
        if isinstance(self.unit, str):
            unit = ExistingQbUnit(unit_uri=self.unit)
        elif isinstance(self.unit, NewUnit):
            unit = _map_unit(self.unit)
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
            elif isinstance(self.measure, NewMeasure):
                measure = _map_measure(self.measure)
            else:
                raise ValueError(f"Unhandled measure type: {self.measure}")

            return QbSingleMeasureObservationValue(
                measure=measure, unit=unit, data_type=self.datatype or "decimal"
            )


def _map_unit(resource: NewUnit) -> NewQbUnit:
    return NewQbUnit(
        label=resource.label,
        description=resource.comment,
        source_uri=resource.isDefinedBy,
        uri_safe_identifier_override=resource.path,
        base_unit=None
        if resource.baseUnit is None
        else ExistingQbUnit(resource.baseUnit),
        base_unit_scaling_factor=resource.baseUnitScalingFactor,
        qudt_quantity_kind_uri=resource.qudtQuantityKind,
        si_base_unit_conversion_multiplier=resource.siBaseUnitConversionMultiplier,
    )


def _map_measure(resource: NewMeasure) -> NewQbMeasure:
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
        columnar_data: List[str] = [
            v for v in pandas_input_to_columnar_optional_str(data) if v is not None
        ]
        return [NewQbAttributeValue(v) for v in sorted(set(columnar_data))]
    elif isinstance(new_attribute_values, list) and len(new_attribute_values) > 0:
        return _map_attribute_values(new_attribute_values)
    elif new_attribute_values is not None:
        raise ValueError(
            f"Unexpected value for 'newAttributeValues': {new_attribute_values}"
        )

    return []
