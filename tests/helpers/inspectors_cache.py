"""
Inspectors Cache
----------------------

Caches inspector objects for data sets which are commonly used as test cases
"""
from pathlib import Path
from typing import Dict

from csvcubed.utils.sparql_handler.data_cube_state import DataCubeState
from csvcubed.utils.tableschema import CsvwRdfManager

_csvw_rdf_manager_cache: Dict[str, CsvwRdfManager] = {}
_data_cube_state_cache: Dict[str, DataCubeState] = {}


def get_csvw_rdf_manager(csvw_json_path: Path) -> CsvwRdfManager:
    path_str = csvw_json_path.resolve().as_uri()
    if path_str not in _csvw_rdf_manager_cache:
        _csvw_rdf_manager_cache[path_str] = CsvwRdfManager(csvw_json_path)

    return _csvw_rdf_manager_cache[path_str]


def get_data_cube_state(csvw_json_path: Path) -> DataCubeState:
    path_str = csvw_json_path.resolve().as_uri()
    if path_str not in _data_cube_state_cache:
        rdf_manager = get_csvw_rdf_manager(csvw_json_path)
        _data_cube_state_cache[path_str] = DataCubeState(rdf_manager.csvw_state)

    return _data_cube_state_cache[path_str]
