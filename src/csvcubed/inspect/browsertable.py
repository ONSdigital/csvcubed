from dataclasses import dataclass
from typing import OrderedDict

import uritemplate

from csvcubed.inspect.browsercolumns import (
    AttributeColumn,
    DataCubeColumn,
    DimensionColumn,
    MeasuresColumn,
    PivotedObservationsColumn,
    StandardShapeObservationsColumn,
    SuppressedColumn,
    UnitsColumn,
    _map_to_data_cube_column,
)
from csvcubed.inspect.browsers import MetadataBrowser, TableBrowser
from csvcubed.inspect.lazyfuncdescriptor import lazy_func_field
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import CatalogMetadataResult
from csvcubed.utils.iterables import single
from csvcubed.utils.qb.components import EndUserColumnType
from csvcubed.utils.sparql_handler.column_component_info import ColumnComponentInfo


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
