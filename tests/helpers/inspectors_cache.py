"""
Inspectors Cache
----------------------

Caches inspector objects for data sets which are commonly used as test cases
"""
from pathlib import Path
from typing import Dict

from csvcubed.utils.sparql_handler.code_list_repository import CodeListRepository
from csvcubed.utils.sparql_handler.data_cube_repository import DataCubeRepository
from csvcubed.utils.tableschema import CsvWRdfManager

_csvw_rdf_manager_cache: Dict[str, CsvWRdfManager] = {}
_data_cube_repository_cache: Dict[str, DataCubeRepository] = {}
_code_list_repository_cache: Dict[str, CodeListRepository] = {}


def get_csvw_rdf_manager(csvw_json_path: Path) -> CsvWRdfManager:
    path_str = csvw_json_path.resolve().as_uri()
    if path_str not in _csvw_rdf_manager_cache:
        _csvw_rdf_manager_cache[path_str] = CsvWRdfManager(csvw_json_path)

    return _csvw_rdf_manager_cache[path_str]


def get_data_cube_repository(csvw_json_path: Path) -> DataCubeRepository:
    path_str = csvw_json_path.resolve().as_uri()
    if path_str not in _data_cube_repository_cache:
        rdf_manager = get_csvw_rdf_manager(csvw_json_path)
        _data_cube_repository_cache[path_str] = DataCubeRepository(
            rdf_manager.csvw_repository
        )

    return _data_cube_repository_cache[path_str]


def get_code_list_repository(csvw_json_path: Path) -> CodeListRepository:
    path_str = csvw_json_path.resolve().as_uri()
    if path_str not in _code_list_repository_cache:
        rdf_manager = get_csvw_rdf_manager(csvw_json_path)
        _code_list_repository_cache[path_str] = CodeListRepository(
            rdf_manager.csvw_repository
        )

    return _code_list_repository_cache[path_str]
