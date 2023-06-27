"""
Inspectors
----------

Class definitions to help provide access to the contents of a CSVW.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cache
from typing import List, Optional, TypeVar

from csvcubed.inspect.lazyfuncdescriptor import lazy_func_field
from csvcubed.inspect.sparql_handler.code_list_repository import CodeListRepository
from csvcubed.inspect.sparql_handler.data_cube_repository import DataCubeRepository
from csvcubed.models.inspect.sparqlresults import CatalogMetadataResult

TClass = TypeVar("TClass")
TRet = TypeVar("TRet")


@dataclass(frozen=True)
class TableInspector(ABC):
    """
    Base table inspector class to be inherited by the DataCubeTable and CodeListTable class
    implementations.
    """

    csv_url: str
    data_cube_repository: DataCubeRepository = field(repr=False)
    code_list_repository: CodeListRepository = field(repr=False)


@dataclass(frozen=True)
class MetadataInspector(ABC):
    """
    Allows access to the various catalog metadata results.
    """

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
