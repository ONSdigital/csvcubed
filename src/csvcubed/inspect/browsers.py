from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import List, Optional, TypeVar, Union

from csvcubed.inspect.browsertable import CodeListTable
from csvcubed.inspect.inspect_api import DataCubeTable
from csvcubed.inspect.lazyfuncdescriptor import lazy_func_field
from csvcubed.models.sparqlresults import CatalogMetadataResult
from csvcubed.utils.sparql_handler.code_list_inspector import CodeListInspector
from csvcubed.utils.sparql_handler.csvw_inspector import CsvWInspector
from csvcubed.utils.sparql_handler.data_cube_inspector import DataCubeInspector
from csvcubed.utils.tableschema import CsvWRdfManager

TClass = TypeVar("TClass")
TRet = TypeVar("TRet")


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
