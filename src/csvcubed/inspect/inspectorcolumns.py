"""
Inspector Columns
-----------------

Class definitions for the several different column types that are used
inside inspector tables.
"""

from abc import ABC
from dataclasses import dataclass, field
from typing import Optional, Union

from csvcubed.definitions import SDMX_ATTRIBUTE_UNIT_URI
from csvcubed.inspect.inspectorcomponents import (
    Attribute,
    Dimension,
    ExternalAttribute,
    ExternalDimension,
    ExternalMeasure,
    ExternalUnit,
    LocalAttribute,
    LocalDimension,
    LocalMeasure,
    LocalUnit,
    Measure,
    Unit,
)
from csvcubed.inspect.lazyfuncdescriptor import lazy_func_field
from csvcubed.inspect.sparql_handler.code_list_repository import CodeListRepository
from csvcubed.inspect.sparql_handler.data_cube_repository import DataCubeRepository
from csvcubed.models.inspect.column_component_info import ColumnComponentInfo
from csvcubed.models.inspect.sparqlresults import QubeComponentResult
from csvcubed.utils.iterables import first, single
from csvcubed.utils.qb.components import ComponentPropertyType, EndUserColumnType


@dataclass(frozen=True)
class DataCubeColumn(ABC):
    """
    Base column class for different data cube column types to inherit from.
    Allows access to the column's info and the data cube/code list repositorys.
    """

    data_cube_repository: DataCubeRepository = field(repr=False)
    code_list_repository: CodeListRepository = field(repr=False)
    info: ColumnComponentInfo = field(repr=False)

    def _get_csv_col_title(self) -> Optional[str]:
        return self.info.column_definition.title

    def _get_cell_uri_template(self) -> Optional[str]:
        return self.info.column_definition.value_url

    def _get_component(self) -> QubeComponentResult:
        component = self.info.component
        if component is None:
            raise ValueError("Could not locate Component")

        return component

    csv_column_title: Optional[str] = lazy_func_field(_get_csv_col_title, repr=False)
    cell_uri_template: Optional[str] = lazy_func_field(
        _get_cell_uri_template, repr=False
    )


@dataclass(frozen=True)
class DimensionColumn(DataCubeColumn):
    """
    Represents a dimension column.
    """

    def _get_dimension(self) -> Dimension:
        dimension_component = self._get_component()

        if (
            dimension_component.property_label is None
            or dimension_component.property_label == ""
        ):
            return ExternalDimension(dimension_component)

        return LocalDimension(dimension_component)

    dimension: Dimension = lazy_func_field(_get_dimension)


@dataclass(frozen=True)
class AttributeColumn(DataCubeColumn):
    """
    Represents an attribute column. Can either exist in the form of a local attribute,
    or an external attribute.
    """

    def _get_attribute(self) -> Attribute:
        attribute_component = self._get_component()
        if (
            attribute_component.property_label is None
            or attribute_component.property_label == ""
        ):
            return ExternalAttribute(attribute_component)

        return LocalAttribute(attribute_component)

    def _get_required(self) -> bool:
        return self._get_component().required

    attribute: Attribute = lazy_func_field(_get_attribute)
    required: bool = lazy_func_field(_get_required)


@dataclass(frozen=True)
class UnitsColumn(DataCubeColumn):
    """
    Represents a Units column
    """

    """TODO: List the units used in this column."""

    pass


@dataclass(frozen=True)
class MeasuresColumn(DataCubeColumn):
    """
    Represents a Measures column
    """

    """TODO: List the measures used in this column."""

    pass


@dataclass(frozen=True)
class ObservationsColumn(DataCubeColumn, ABC):
    """
    Represents an observation column. Can exist either as a pivoted shape observation column,
    or a standard shape observation column.
    """

    def _get_unit(self) -> Union[Unit, UnitsColumn]:
        columns_in_csv = (
            self.data_cube_repository.csvw_repository.get_column_definitions_for_csv(
                self.info.column_definition.csv_url
            )
        )

        unit_uri = first(
            c.value_url
            for c in columns_in_csv
            if c.virtual
            and c.property_url == SDMX_ATTRIBUTE_UNIT_URI
            and c.about_url == self.info.column_definition.about_url
        )
        if unit_uri is None:
            # There must be a units column for this obs val column.
            column_component_infos = (
                self.data_cube_repository.get_column_component_info(
                    self.info.column_definition.csv_url
                )
            )
            units_column_info = single(
                column_component_infos,
                lambda c: c.column_type == EndUserColumnType.Units
                and c.column_definition.about_url
                == self.info.column_definition.about_url,
            )
            return UnitsColumn(
                data_cube_repository=self.data_cube_repository,
                code_list_repository=self.code_list_repository,
                info=units_column_info,
            )

        local_unit = self.data_cube_repository.get_unit_for_uri(unit_uri)
        if local_unit is None:
            return ExternalUnit(unit_uri)

        return LocalUnit(unit_uri=local_unit.unit_uri, label=local_unit.unit_label)

    unit: Union[Unit, UnitsColumn] = lazy_func_field(_get_unit)


@dataclass(frozen=True)
class PivotedObservationsColumn(ObservationsColumn):
    """
    Represents an observations column in a pivoted shape data cube, extending the Observations
    column's implementation.
    """

    def _get_measure(self) -> Measure:
        measure_uri = self.info.column_definition.property_url
        if measure_uri is None:
            raise ValueError("Measure URI was not set.")

        local_measure_component = first(
            c
            for c in self.data_cube_repository.get_dsd_qube_components_for_csv(
                self.info.column_definition.csv_url
            ).qube_components
            if c.property_type == ComponentPropertyType.Measure.value
            and c.property == measure_uri
        )

        if local_measure_component is None:
            return ExternalMeasure(measure_uri)

        measure_label = local_measure_component.property_label
        if measure_label is None:
            raise ValueError("Local measure's label is not set.")

        return LocalMeasure(measure_uri=measure_uri, label=measure_label)

    measure: Measure = lazy_func_field(_get_measure)


@dataclass(frozen=True)
class StandardShapeObservationsColumn(ObservationsColumn):
    """
    Represents an observations column in a standard shape data cube, extending the observations
    column's implementation.
    """

    def _get_measures_column(self) -> MeasuresColumn:
        measure_col_info = single(
            c
            for c in self.data_cube_repository.get_column_component_info(
                self.info.column_definition.csv_url
            )
            if c.column_type == EndUserColumnType.Measures
        )

        return MeasuresColumn(
            data_cube_repository=self.data_cube_repository,
            code_list_repository=self.code_list_repository,
            info=measure_col_info,
        )

    measures_column: MeasuresColumn = lazy_func_field(_get_measures_column)


@dataclass(frozen=True)
class SuppressedColumn(DataCubeColumn):
    """
    Represents a column that has its output suppressed.
    """

    pass
