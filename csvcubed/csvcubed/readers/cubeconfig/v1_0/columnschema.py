"""
Models
------

config.json V1.0 column mapping models.
"""
import uritemplate

from typing import List, TypeVar

from csvcubed.models.cube import *
from csvcubed.models.cube.qb.components import *
from csvcubed.inputs import (
    PandasDataTypes,
    pandas_input_to_columnar_optional_str,
)
from csvcubed.utils.uri import (
    csvw_column_name_safe,
    looks_like_uri,
)
from csvcubedmodels.dataclassbase import DataClassBase

T = TypeVar("T", bound=object)


@dataclass
class SchemaBaseClass(DataClassBase, ABC):
    ...


@dataclass
class NewDimension(SchemaBaseClass):
    # Schema property - but removed for json to dataclass mapping
    # type: # str = "dimension"

    # Properties only available for New Dimension
    label: str
    description: Optional[str] = None
    definition_uri: Optional[str] = None

    # Properties common to both New and Existing Dimension
    from_existing: Optional[str] = None
    cell_uri_template: Optional[str] = None
    code_list: Optional[Union[str, bool]] = True

    def map_to_new_qb_dimension(
        self, label: str, data: PandasDataTypes
    ) -> NewQbDimension:

        new_dimension = NewQbDimension.from_data(
            label=self.label or label,
            data=data,
            description=self.description,
            parent_dimension_uri=self.from_existing,
            source_uri=self.definition_uri,
        )
        # The NewQbCodeList and Concepts are populated in the NewQbDimension.from_data() call
        # the _get_code_list method overrides the code_list if required.
        new_dimension.code_list = self._get_code_list(new_dimension)
        return new_dimension

    def _get_code_list(
        self,
        new_dimension: NewQbDimension
    ) -> Optional[QbCodeList]:

        code_list_obj = None

        if isinstance(self.code_list, str):
            if looks_like_uri(self.code_list):
                code_list_obj = ExistingQbCodeList(self.code_list)

            else:
                raise ValueError("Code List contains a string that cannot be recognised as a URI")

        elif isinstance(self.code_list, bool):
            if self.code_list is False:
                code_list_obj = None

            elif (
                new_dimension.parent_dimension_uri
                == "http://purl.org/linked-data/sdmx/2009/dimension#refPeriod"
                and self.definition_uri is not None
                and self.definition_uri.lower().startswith("http://reference.data.gov.uk/id/")
            ):
                # This is a special case where we build up a code-list of the date/time values.
                code_list_obj = self._get_date_time_code_list_for_dimension(
                    self.label, new_dimension
                )
                # else, the user wants a standard codelist to be automatically generated
                return code_list_obj or new_dimension.code_list
        else:
            raise ValueError(f"Unmatched code_list value {self.code_list}")

        return code_list_obj or new_dimension.code_list

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
                        c.value,
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
    from_existing: str
    cell_uri_template: Optional[str] = None

    def map_to_existing_qb_dimension(self) -> ExistingQbDimension:
        return ExistingQbDimension(dimension_uri=self.from_existing)


@dataclass
class AttributeValue(SchemaBaseClass):
    label: str
    description: Optional[str] = None
    from_existing: Optional[str] = None
    definition_uri: Optional[str] = None


@dataclass
class ExistingAttribute(SchemaBaseClass):
    from_existing: str
    definition_uri: Optional[str] = None
    data_type: Optional[str] = None
    required: bool = False
    values: Union[bool, List[AttributeValue]] = True

    def map_to_existing_qb_attribute(
        self, data: PandasDataTypes
    ) -> Union[ExistingQbAttribute, ExistingQbAttributeLiteral]:

        if self.data_type is None:
            return ExistingQbAttribute(
                self.from_existing,
                new_attribute_values=_get_new_attribute_values(data, self.values),
                is_required=self.required,
            )

        else:
            if self.values:
                raise Exception(
                    "Attributes cannot represent both literal values and attribute (resource) values"
                )
            return ExistingQbAttributeLiteral(
                attribute_uri=self.from_existing,
                data_type=self.data_type,
                is_required=self.required,
            )


@dataclass
class NewAttribute(SchemaBaseClass):
    label: str
    description: Optional[str] = None
    from_existing: Optional[str] = None
    definition_uri: Optional[str] = None
    data_type: Optional[str] = None
    required: bool = False
    values: Union[bool, List[AttributeValue]] = True

    def map_to_new_qb_attribute(
        self, column_title: str, data: PandasDataTypes
    ) -> NewQbAttribute:
        if isinstance(self, NewAttribute) and self.data_type is not None:
            if isinstance(self.values, list):
                raise Exception(
                    "Attributes cannot represent both literal values and attribute (resource) values"
                )
            return NewQbAttributeLiteral(
                label=self.label,
                description=self.description,
                data_type=self.data_type,
                parent_attribute_uri=self.from_existing,
                source_uri=self.definition_uri,
                is_required=self.required,
            )
        else:
            if isinstance(self.values, bool) and self.values is True:
                return NewQbAttribute.from_data(
                    label=self.label or column_title,
                    data=data,
                    description=self.description,
                    parent_attribute_uri=self.from_existing,
                    source_uri=self.definition_uri,
                    is_required=self.required,
                )

            elif isinstance(self, NewAttribute):
                return NewQbAttribute(
                    label=self.label or column_title,
                    description=self.description,
                    new_attribute_values=_get_new_attribute_values(data, self.values),
                    parent_attribute_uri=self.from_existing,
                    source_uri=self.definition_uri,
                    is_required=self.required
                )
            else:
                raise ValueError(f"Unhandled value: {self}")


@dataclass
class Unit(SchemaBaseClass):
    label: str
    description: Optional[str] = None
    from_existing: Optional[str] = None
    definition_uri: Optional[str] = None
    scaling_factor: Optional[float] = None
    si_scaling_factor: Optional[float] = None
    quantity_kind: Optional[str] = None


@dataclass
class ExistingUnits(SchemaBaseClass):
    cell_uri_template: str
    values: Union[bool, List[Unit]] = True

    def map_to_existing_qb_multi_units(
        self, data: PandasDataTypes, column_title: str
    ) -> QbMultiUnits:
        return QbMultiUnits.existing_units_from_data(
            data, csvw_column_name_safe(column_title), self.cell_uri_template
        )


@dataclass
class NewUnits(SchemaBaseClass):
    values: Union[bool, List[Unit]] = True

    def map_to_new_qb_multi_units(self, data: PandasDataTypes) -> QbMultiUnits:
        if isinstance(self.values, bool) and self.values is True:
            return QbMultiUnits.new_units_from_data(data)

        elif isinstance(self.values, list):

            units = []
            for unit in self.values:
                if not isinstance(unit, Unit):
                    raise ValueError(f"Unexpected unit value: {unit}")

                units.append(_map_unit(unit))

            return QbMultiUnits(units)

        raise ValueError(f"Unhandled 'Units' value: {self}")


@dataclass
class Measure(SchemaBaseClass):
    label: str
    description: Optional[str] = None
    from_existing: Optional[str] = None
    definition_uri: Optional[str] = None


@dataclass
class NewMeasures(SchemaBaseClass):
    values: Union[bool, List[Measure]] = True

    def map_to_new_multi_measure_dimension(
        self, data: PandasDataTypes
    ) -> QbMultiMeasureDimension:
        # When values is a single bool True then create new Measures from the csv column data
        if self.values is True:
            return QbMultiMeasureDimension.new_measures_from_data(data)

        elif isinstance(self.values, list):
            new_measures: List[QbMeasure] = []
            for new_measure in self.values:
                if not isinstance(new_measure, Measure):
                    raise ValueError(f"Unexpected measure: {new_measure}")
                else:
                    new_measures.append(NewQbMeasure.from_dict(new_measure.as_dict()))

            return QbMultiMeasureDimension(new_measures)

        else:
            raise ValueError(f"Unexpected values type: {self.values}")


@dataclass
class ExistingMeasures(SchemaBaseClass):
    cell_uri_template: str
    values: Union[bool, List[Measure]] = True

    def map_to_existing_multi_measure_dimension(
        self, column_title: str, data: PandasDataTypes
    ) -> QbMultiMeasureDimension:
        csvw_column_name = csvw_column_name_safe(column_title)
        return QbMultiMeasureDimension.existing_measures_from_data(
            data, csvw_column_name, self.cell_uri_template
        )


@dataclass
class ObservationValue(SchemaBaseClass):
    datatype: str = "decimal"
    unit: Union[None, str, Unit] = None
    measure: Union[None, str, Measure] = None

    def map_to_qb_observation(self) -> QbObservationValue:
        unit = None
        if isinstance(self.unit, str):
            unit = ExistingQbUnit(unit_uri=self.unit)

        elif isinstance(self.unit, Unit):
            unit = _map_unit(self.unit)

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

            elif isinstance(self.measure, Measure):
                measure = _map_measure(self.measure)

            else:
                raise ValueError(f"Unhandled measure type: {self.measure}")

            return QbSingleMeasureObservationValue(
                measure=measure, unit=unit, data_type=self.datatype or "decimal"
            )


def _map_unit(resource: Unit) -> NewQbUnit:
    return NewQbUnit(
        label=resource.label,
        description=resource.description,
        source_uri=resource.from_existing,
        base_unit=(
            None if resource.from_existing is None else ExistingQbUnit(resource.from_existing)
        ),
        base_unit_scaling_factor=resource.scaling_factor,
        qudt_quantity_kind_uri=resource.quantity_kind,
        si_base_unit_conversion_multiplier=resource.si_scaling_factor,
    )


def _map_measure(resource: Measure) -> NewQbMeasure:
    return NewQbMeasure(
        label=resource.label,
        description=resource.description,
        source_uri=resource.definition_uri,
        parent_measure_uri=resource.from_existing,
    )


def _map_attribute_values(
    new_attribute_values_from_schema: List[AttributeValue],
) -> List[NewQbAttributeValue]:
    new_attribute_values = []
    for attr_val in new_attribute_values_from_schema:
        if not isinstance(attr_val, AttributeValue):
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
    new_attribute_values: Union[None, bool, List[AttributeValue]],
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
