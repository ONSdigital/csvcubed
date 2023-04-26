from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import (
    Any,
    Callable,
    Generic,
    List,
    Mapping,
    Optional,
    OrderedDict,
    Type,
    TypeVar,
    Union,
)

import uritemplate

from csvcubed.definitions import SDMX_ATTRIBUTE_UNIT_URI
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import CatalogMetadataResult, QubeComponentResult
from csvcubed.utils.iterables import first, single
from csvcubed.utils.qb.components import ComponentPropertyType, EndUserColumnType
from csvcubed.utils.sparql_handler.code_list_inspector import CodeListInspector
from csvcubed.utils.sparql_handler.column_component_info import ColumnComponentInfo
from csvcubed.utils.sparql_handler.csvw_inspector import CsvWInspector
from csvcubed.utils.sparql_handler.data_cube_inspector import DataCubeInspector
from csvcubed.utils.tableschema import CsvWRdfManager

TClass = TypeVar("TClass")
TRet = TypeVar("TRet")


class LazyFuncFieldDescriptor(Generic[TClass, TRet]):
    """
    https://docs.python.org/3/library/dataclasses.html#descriptor-typed-fields
    """

    def __init__(self, gen: Callable[[TClass], TRet]):
        self._gen = gen

    def __set_name__(self, owner, name):
        ...

    def __get__(self, instance: Optional[TClass], t: Type) -> TRet:
        if instance is None:
            # Tell the data class that there is no default value.
            raise AttributeError()

        return self._gen(instance)

    def __set__(self, instance: Any, value: Any) -> None:
        raise NotImplementedError()


def lazy_func_field(
    value_generator: Callable[[TClass], TRet],
    repr: bool = True,
    hash: Optional[bool] = None,
    compare: bool = False,
    metadata: Optional[Mapping] = None,
) -> TRet:
    """
    Allows you to define a dataclass field which returns the value of a function evaluated (lazily) upon accessing the
    attribute.

    These fields are read-only.

    We lie a bit about the return type so that pyright will be happy type checking our functions.
    """
    return field(
        init=False,
        default=LazyFuncFieldDescriptor(value_generator),
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=metadata,
    )  # type: ignore


@dataclass(frozen=True)
class TableBrowser(ABC):
    csv_url: str
    data_cube_inspector: DataCubeInspector = field(repr=False)
    code_list_inspector: CodeListInspector = field(repr=False)


@dataclass(frozen=True)
class MetadataBrowser(ABC):
    def _get_title(self) -> str:
        return self._get_metadata().title

    def _get_description(self) -> Optional[str]:
        return self._get_metadata().description

    def _get_issued(self) -> Optional[str]:
        return self._get_metadata().issued

    def _get_modified(self) -> Optional[str]:
        return self._get_metadata().modified

    def _get_license(self) -> Optional[str]:
        return self._get_metadata().license

    def _get_creator(self) -> Optional[str]:
        return self._get_metadata().creator

    def _get_publisher(self) -> Optional[str]:
        return self._get_metadata().publisher

    def _get_landing_pages(self) -> List[str]:
        return self._get_metadata().landing_pages

    def _get_themes(self) -> List[str]:
        return self._get_metadata().themes

    def _get_keywords(self) -> List[str]:
        return self._get_metadata().keywords

    def _get_contact_point(self) -> Optional[str]:
        return self._get_metadata().contact_point

    def _get_comment(self) -> Optional[str]:
        return self._get_metadata().comment

    title: str = lazy_func_field(_get_title)
    description: Optional[str] = lazy_func_field(_get_description, repr=False)
    issued: Optional[str] = lazy_func_field(_get_issued, repr=False)
    modified: Optional[str] = lazy_func_field(_get_modified, repr=False)
    license: Optional[str] = lazy_func_field(_get_license, repr=False)
    creator: Optional[str] = lazy_func_field(_get_creator, repr=False)
    publisher: Optional[str] = lazy_func_field(_get_publisher, repr=False)
    landing_pages: List[str] = lazy_func_field(_get_landing_pages, repr=False)
    themes: List[str] = lazy_func_field(_get_themes, repr=False)
    keywords: List[str] = lazy_func_field(_get_keywords, repr=False)
    contact_point: Optional[str] = lazy_func_field(_get_contact_point, repr=False)
    comment: Optional[str] = lazy_func_field(_get_comment, repr=False)

    @cache
    @abstractmethod
    def _get_metadata(self) -> CatalogMetadataResult:
        """
        Must return the catalogue metadata describing this entity.
        """
        ...

    @abstractmethod
    def __hash__(self):
        pass


@dataclass(frozen=True)
class DataCubeColumn(ABC):
    data_cube_inspector: DataCubeInspector = field(repr=False)
    code_list_inspector: CodeListInspector = field(repr=False)
    info: ColumnComponentInfo = field(repr=False)

    def _get_csv_col_title(self) -> Optional[str]:
        return self.info.column_definition.title

    def _get_cell_uri_template(self) -> Optional[str]:
        return self.info.column_definition.value_url

    csv_column_title: Optional[str] = lazy_func_field(_get_csv_col_title, repr=False)
    cell_uri_template: Optional[str] = lazy_func_field(
        _get_cell_uri_template, repr=False
    )


@dataclass(frozen=True)
class Dimension:
    dimension_component: QubeComponentResult = field(repr=False)

    def _get_dimension_uri(self) -> str:
        return self.dimension_component.property

    dimension_uri: str = lazy_func_field(_get_dimension_uri)


@dataclass(frozen=True)
class ExternalDimension(Dimension):
    """A dimension defined externally to this data set."""

    pass


@dataclass(frozen=True)
class LocalDimension(Dimension):
    """A dimension which is defined locally in this data set."""

    def _get_label(self):
        dimension_label = self.dimension_component.property_label
        if dimension_label is None:
            raise ValueError("Could not locate label for locally defined dimension")

        return dimension_label

    label: str = lazy_func_field(_get_label)

    # todo: Should bring parent/subPropertyOf value in here.


@dataclass(frozen=True)
class DimensionColumn(DataCubeColumn):
    def _get_dimension(self) -> Dimension:
        dimension_component = self.info.component
        if dimension_component is None:
            raise ValueError("Could not locate Dimension Component")

        if dimension_component.property_label is None:
            return ExternalDimension(dimension_component)

        return LocalDimension(dimension_component)

    dimension: Dimension = lazy_func_field(_get_dimension)


@dataclass(frozen=True)
class Attribute:
    attribute_component: QubeComponentResult = field(repr=False)

    def _get_attribute_uri(self) -> str:
        return self.attribute_component.property

    attribute_uri: str = lazy_func_field(_get_attribute_uri)


@dataclass(frozen=True)
class ExternalAttribute(Attribute):
    """An attribute defined externally to this data set."""

    pass


@dataclass(frozen=True)
class LocalAttribute(Attribute):
    """An attribute which is defined locally in this data set."""

    def _get_label(self):
        attribute_label = self.attribute_component.property_label
        if attribute_label is None:
            raise ValueError("Could not locate label for locally defined dimension")

        return attribute_label

    label: str = lazy_func_field(_get_label)

    # todo: Should bring parent/subPropertyOf value in here.


@dataclass(frozen=True)
class AttributeColumn(DataCubeColumn):
    def _get_component(self) -> QubeComponentResult:
        attribute_component = self.info.component
        if attribute_component is None:
            raise ValueError("Could not locate Attribute Component")

        return attribute_component

    def _get_attribute(self) -> Attribute:
        attribute_component = self._get_component()
        if attribute_component.property_label is None:
            return ExternalAttribute(attribute_component)

        return LocalAttribute(attribute_component)

    def _get_required(self) -> bool:
        return self._get_component().required

    attribute: Attribute = lazy_func_field(_get_attribute)
    required: bool = lazy_func_field(_get_required)


@dataclass(frozen=True)
class UnitsColumn(DataCubeColumn):
    """TODO: List the units used in this column."""

    pass


@dataclass(frozen=True)
class MeasuresColumn(DataCubeColumn):
    """TODO: List the measures used in this column."""

    pass


@dataclass(frozen=True)
class Unit:
    unit_uri: str


@dataclass(frozen=True)
class ExternalUnit(Unit):
    """A unit defined externally to this data set."""

    pass


@dataclass(frozen=True)
class LocalUnit(Unit):
    """A unit which is defined locally in this data set."""

    label: str

    # todo: Should bring parent/subPropertyOf value in here.


@dataclass(frozen=True)
class ObservationsColumn(DataCubeColumn, ABC):
    def _get_unit(self) -> Union[Unit, UnitsColumn]:
        columns_in_csv = (
            self.data_cube_inspector.csvw_inspector.get_column_definitions_for_csv(
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
            column_component_infos = self.data_cube_inspector.get_column_component_info(
                self.info.column_definition.csv_url
            )
            units_column_info = single(
                column_component_infos,
                lambda c: c.column_type == EndUserColumnType.Units
                and c.column_definition.about_url
                == self.info.column_definition.about_url,
            )
            return UnitsColumn(
                data_cube_inspector=self.data_cube_inspector,
                code_list_inspector=self.code_list_inspector,
                info=units_column_info,
            )

        local_unit = self.data_cube_inspector.get_unit_for_uri(unit_uri)
        if local_unit is None:
            return ExternalUnit(unit_uri)

        return LocalUnit(unit_uri=local_unit.unit_uri, label=local_unit.unit_label)

    unit: Union[Unit, UnitsColumn] = lazy_func_field(_get_unit)


@dataclass(frozen=True)
class Measure:
    measure_uri: str


@dataclass(frozen=True)
class ExternalMeasure(Measure):
    """A measure defined externally to this data set."""

    pass


@dataclass(frozen=True)
class LocalMeasure(Measure):
    """A measure which is defined locally in this data set."""

    label: str

    # todo: Should bring parent/subPropertyOf value in here.


@dataclass(frozen=True)
class PivotedObservationsColumn(ObservationsColumn):
    def _get_measure(self) -> Measure:
        measure_uri = self.info.column_definition.property_url
        if measure_uri is None:
            raise ValueError("Measure URI was not set.")

        local_measure_component = first(
            c
            for c in self.data_cube_inspector.get_dsd_qube_components_for_csv(
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
    def _get_measures_column(self) -> MeasuresColumn:
        measure_col_info = single(
            c
            for c in self.data_cube_inspector.get_column_component_info(
                self.info.column_definition.csv_url
            )
            if c.column_type == EndUserColumnType.Measures
        )

        return MeasuresColumn(
            data_cube_inspector=self.data_cube_inspector,
            code_list_inspector=self.code_list_inspector,
            info=measure_col_info,
        )

    measures_column: MeasuresColumn = lazy_func_field(_get_measures_column)


@dataclass(frozen=True)
class SuppressedColumn(DataCubeColumn):
    pass


def _map_to_data_cube_column(
    table_browser: TableBrowser, info: ColumnComponentInfo
) -> DataCubeColumn:
    if info.column_type == EndUserColumnType.Dimension:
        return DimensionColumn(
            data_cube_inspector=table_browser.data_cube_inspector,
            code_list_inspector=table_browser.code_list_inspector,
            info=info,
        )
    elif info.column_type == EndUserColumnType.Attribute:
        return AttributeColumn(
            data_cube_inspector=table_browser.data_cube_inspector,
            code_list_inspector=table_browser.code_list_inspector,
            info=info,
        )
    elif info.column_type == EndUserColumnType.Units:
        return UnitsColumn(
            data_cube_inspector=table_browser.data_cube_inspector,
            code_list_inspector=table_browser.code_list_inspector,
            info=info,
        )
    elif info.column_type == EndUserColumnType.Measures:
        return MeasuresColumn(
            data_cube_inspector=table_browser.data_cube_inspector,
            code_list_inspector=table_browser.code_list_inspector,
            info=info,
        )
    elif info.column_type == EndUserColumnType.Observations:
        if info.column_definition.property_url is not None and any(
            uritemplate.variables(info.column_definition.property_url)
        ):
            return StandardShapeObservationsColumn(
                data_cube_inspector=table_browser.data_cube_inspector,
                code_list_inspector=table_browser.code_list_inspector,
                info=info,
            )
        else:
            return PivotedObservationsColumn(
                data_cube_inspector=table_browser.data_cube_inspector,
                code_list_inspector=table_browser.code_list_inspector,
                info=info,
            )
    elif info.column_type == EndUserColumnType.Suppressed:
        return SuppressedColumn(
            data_cube_inspector=table_browser.data_cube_inspector,
            code_list_inspector=table_browser.code_list_inspector,
            info=info,
        )
    raise ValueError(
        f"Unmatched column type {info.column_type} with column title {info.column_definition.title}"
    )


@dataclass(frozen=True)
class DataCubeTable(MetadataBrowser, TableBrowser):
    def _get_shape(self) -> CubeShape:
        return self.data_cube_inspector.get_shape_for_csv(self.csv_url)

    def _get_dataset_uri(self) -> str:
        return self.data_cube_inspector.get_cube_identifiers_for_csv(
            self.csv_url
        ).data_set_url

    def _get_columns(self) -> OrderedDict[str, DataCubeColumn]:
        columns = OrderedDict[str, DataCubeColumn]()
        for c in self.data_cube_inspector.get_column_component_info(self.csv_url):
            if c.column_definition.title is not None:
                columns[c.column_definition.title] = _map_to_data_cube_column(self, c)

        return columns

    shape: CubeShape = lazy_func_field(_get_shape)
    data_set_uri: str = lazy_func_field(_get_dataset_uri)
    columns: OrderedDict[str, DataCubeColumn] = lazy_func_field(
        _get_columns, repr=False
    )

    def __hash__(self):
        return hash(self.csv_url)

    def _get_metadata(self) -> CatalogMetadataResult:
        data_set_url = self._get_dataset_uri()
        return single(
            self.data_cube_inspector.csvw_inspector.catalog_metadata,
            lambda c: c.dataset_uri == data_set_url,
        )


@dataclass(frozen=True)
class CodeListTable(MetadataBrowser, TableBrowser):
    def _get_concept_scheme_uri(self) -> str:
        return single(
            self.code_list_inspector._code_list_table_identifiers,
            lambda i: i.csv_url == self.csv_url,
        ).concept_scheme_url

    concept_scheme_uri: str = lazy_func_field(_get_concept_scheme_uri)

    def __hash__(self):
        return hash(self.csv_url)

    def _get_metadata(self) -> CatalogMetadataResult:
        return self.code_list_inspector.get_catalog_metadata_for_concept_scheme(
            self._get_concept_scheme_uri()
        )


@dataclass
class CsvWBrowser:
    primary_csvw: Union[str, Path]
    _csvw_inspector: CsvWInspector = field(init=False, repr=False)
    _data_cube_inspector: DataCubeInspector = field(init=False, repr=False)
    _code_list_inspector: CodeListInspector = field(init=False, repr=False)

    def _get_tables(self) -> List[TableBrowser]:
        cube_tables = [
            DataCubeTable(
                csv_url=t.csv_url,
                data_cube_inspector=self._data_cube_inspector,
                code_list_inspector=self._code_list_inspector,
            )
            for t in self._data_cube_inspector._cube_table_identifiers.values()
        ]
        code_list_tables = [
            CodeListTable(
                csv_url=t.csv_url,
                data_cube_inspector=self._data_cube_inspector,
                code_list_inspector=self._code_list_inspector,
            )
            for t in self._code_list_inspector._code_list_table_identifiers
        ]

        return [*cube_tables, *code_list_tables]

    tables: List[TableBrowser] = lazy_func_field(_get_tables)

    def __post_init__(self):
        csvw_path = (
            self.primary_csvw
            if isinstance(self.primary_csvw, Path)
            else Path(self.primary_csvw)
        )
        csvw_rdf_manager = CsvWRdfManager(csvw_path.expanduser())
        self._csvw_inspector = csvw_rdf_manager.csvw_inspector
        self._data_cube_inspector = DataCubeInspector(self._csvw_inspector)
        self._code_list_inspector = CodeListInspector(self._csvw_inspector)
