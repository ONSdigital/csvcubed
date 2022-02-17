"""
Models
------

config.json V1.0 column mapping models.
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
class Dimension(SchemaBaseClass):
    # Schema property - but removed for json to dataclass mapping
    # type: # str = "dimension"

    # Properties only available for New Dimension
    label: Optional[str]
    description: Optional[str]
    definition_uri: Optional[str]

    # Properties common to both New and Existing Dimension
    from_existing: Optional[str]
    cell_uri_template: Optional[str]
    code_list: Optional[Union[str, bool]]

    def map_to_qb_dimension(
        self, label: str, data: PandasDataTypes, json_parent_dir: Path
    ) -> Union[NewQbDimension, ExistingQbDimension]:

        # No label, description or code_list means its likely to be an ExistingDimension
        if not any(self.label, self.description, self.code_list):
            # but requires a valid from_existing uri str
            if isinstance(self.from_existing, str) and looks_like_uri(
                self.from_existing
            ):
                return ExistingQbDimension(self.from_existing)
            else:
                raise ValueError(
                    "Existing Dimension - from_existing property was not a valid URI"
                )

        # label, description or code_list present therefore it will be a NewDimension
        else:
            new_dimension = NewQbDimension.from_data(
                label=label,
                data=data,
                description=self.description,
                parent_dimension_uri=self.from_existing,
                source_uri=self.definition_uri,
            )
            new_dimension.code_list = self._get_code_list()

            return new_dimension

    def _get_code_list(
        self, json_parent_dir: Path
    ) -> Union[NewQbCodeListInCsvW, ExistingQbCodeList]:

        code_list_obj = None

        if isinstance(self.code_list, str):
            if looks_like_uri(self.code_list):
                return ExistingQbCodeList(self.code_list)

            else:
                code_list_path = Path(self.code_list)
                if code_list_path.is_absolute():
                    code_list_obj = NewQbCodeListInCsvW(code_list_path)

                else:
                    code_list_obj = NewQbCodeListInCsvW(
                        json_parent_dir / self.code_list
                    )

        elif isinstance(self.code_list, bool):
            if self.code_list is False:
                code_list_obj = None

            elif (
                # self.subPropertyOf ==
                # "http://purl.org/linked-data/sdmx/2009/dimension#refPeriod"
                # and
                self.code_list is not None
                and self.code_list.lower().startswith(
                    "http://reference.data.gov.uk/id/"
                )
            ):
                # This is a special case where we build up a code-list of the date/time values.
                code_list_obj = self._get_date_time_code_list_for_dimension(
                    self.label, self.new_dimension
                )
            # else, the user wants a standard codelist to be automatically generated
        else:
            raise ValueError(f"Unmatched code_list value {self.code_list}")

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
class NewAttributeValue(SchemaBaseClass):
    label: str
    description: Optional[str] = None
    from_existing: Optional[str] = None
    definition_uri: Optional[str] = None


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
class Attribute(SchemaBaseClass):
    label: str
    description: Optional[str] = None
    from_existing: Optional[str] = None
    definition_uri: Optional[str] = None
    data_type: Optional[str] = None
    required: Optional[bool] = None
    values: Union[bool, List[NewAttributeValue]] = None

    def map_to_qb_attribute(
        self, label: str, data: PandasDataTypes
    ) -> Union[NewQbAttribute, ExistingQbAttribute]:
        pass

    def map_to_qb_attribute(self, column_title: str, data: PandasDataTypes):
        if any(self.label, self.description, self. definition_uri) is True:
            # It will be a NewAttribute
            return self.map_to_new_qb_attribute(self.label, self.data)

        else:
            # It will be an ExistingAttribute
            return self.map_to_existing_qb_attribute(self.data)


    def map_to_new_qb_attribute(
        self, column_title: str, data: PandasDataTypes
    ) -> NewQbAttribute:
        if (
            isinstance(self, NewAttributeProperty)
            and self.data_type is not None
        ):
            if self.newAttributeValues:
                raise Exception(
                    "Attributes cannot represent both literal values and attribute (resource) values"
                )
            return NewQbAttributeLiteral(
                label=self.label,
                description=self.description,
                data_type=self.data_type,
                parent_attribute_uri=self.from_existing,
                source_uri=self.definition_uri,
                is_required=self.isRequired
            )
        else:
            if isinstance(self.values, bool) and self.values is True:
                return NewQbAttribute.from_data(
                    label=column_title, data=data, is_required=self.isRequired
                )

            elif isinstance(self, NewAttributeProperty):
                return NewQbAttribute(
                    label=self.label,
                    description=self.description,
                    new_attribute_values=_get_new_attribute_values(
                        data, self.values
                    ),
                    parent_attribute_uri=self.from_existing,
                    source_uri=self.definition_uri,
                    is_required=self.required
                )
            else:
                raise ValueError(f"Unhandled value: {self}")

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
                data_type=self.data_type,
                is_required=self.required,
            )


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
class UnitType(SchemaBaseClass):
    label: str
    description: Optional[str] = None
    from_existing: Optional[str] = None
    definition_uri: Optional[str] = None
    scaling_factor: Optional[float] = None
    si_scaling_factor: Optional[float] = None
    quantity_kind: Optional[str] = None


@dataclass
class Units(SchemaBaseClass):
    values: Union[bool, List[UnitType]] = True

    def map_to_qb_multi_units(self, data: PandasDataTypes) -> QbMultiUnits:
        if isinstance(self.values, bool) and self.values is True:
            return QbMultiUnits.new_units_from_data(data)

        elif isinstance(self.values, list):

            units = []
            for unit in self.values:
                if not isinstance(unit, UnitType):
                    raise ValueError(f"Unexpected unit value: {unit}")

                if any(unit.label, unit.description, unit.definition_uri):
                    # NewUnit
                    units.append(_map_unit(unit))

                elif unit.from_existing:
                    units.append(ExistingQbUnit(unit_uri=self.values.from_existing))

                else:
                    raise ValueError(f"Unexpected unit value: {unit}")

            return QbMultiUnits(units)

        raise ValueError(f"Unhandled 'Units' value: {self}")


@dataclass
class MeasureType(SchemaBaseClass):
    label: str
    description: Optional[str] = None
    from_existing: Optional[str] = None
    definition_uri: Optional[str] = None


@dataclass
class Measures(SchemaBaseClass):
    values: Union[bool, MeasureType]

    def map_to_multi_measure_dimension(
        self, data: PandasDataTypes
    ) -> QbMultiMeasureDimension:
        # When values is a single bool True then create new Measures from the csv column data
        if self.values is True:
            return QbMultiMeasureDimension.new_measures_from_data(data)

        elif isinstance(self.values, list):
            new_measures = []
            for new_measure in self.values:
                if not isinstance(new_measure, MeasureType):
                    raise ValueError(f"Unexpected measure: {new_measure}")

                if any(new_measure.label, new_measure.description, new_measure.definition_uri):
                    # NewQBMeasure
                    new_measures.append(_map_measure(new_measure))
                else:
                    new_measures.append(QbMultiMeasureDimension(new_measure))

            return QbMultiMeasureDimension(new_measures)

        else:
            raise ValueError(f"Unexpected values type: {self.values}")


@dataclass
class ObservationValue(SchemaBaseClass):
    datatype: Optional[str] = None
    unit: Union[None, str, Units] = None
    measure: Union[None, str, Measures] = None

    def map_to_qb_observation(self) -> QbObservationValue:
        unit = None
        if isinstance(self.unit, str):
            unit = ExistingQbUnit(unit_uri=self.unit)

        elif isinstance(self.unit, Units):
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

            elif isinstance(self.measure, Measures):
                measure = _map_measure(self.measure)

            else:
                raise ValueError(f"Unhandled measure type: {self.measure}")

            return QbSingleMeasureObservationValue(
                measure=measure, unit=unit, data_type=self.datatype or "decimal"
            )


def _map_unit(resource: Units) -> NewQbUnit:
    return NewQbUnit(
        label=resource.label,
        description=resource.description,
        source_uri=resource.from_existing,
        # uri_safe_identifier_override=resource.path,
        base_unit=(
                      None
                      if resource.baseUnit is None
                      else ExistingQbUnit(resource.baseUnit)
                  ),
        base_unit_scaling_factor=resource.scaling_Factor,
        qudt_quantity_kind_uri=resource.quantity_kind,
        si_base_unit_conversion_multiplier=resource.si_scaling_factor,
    )


def _map_measure(resource: MeasureType) -> NewQbMeasure:
    return NewQbMeasure(
        label=resource.label,
        description=resource.description,
        source_uri=resource.definition_uri,
        parent_measure_uri=resource.from_existing,
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
                description=attr_val.description,
                source_uri=attr_val.definition_uri,
                # uri_safe_identifier_override=attr_val.path,
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
