from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Dict, List, Any

import rdflib
from csvcubed.models.cube.cube_shape import CubeShape

from csvcubed.models.sparqlresults import ColTitlesAndNamesResult, DSDLabelURIResult, ObservationValueColumnTitleAboutUrlResult, QubeComponentsResult, UnitColumnAboutValueUrlResult
from csvcubed.utils.sparql_handler.sparqlmanager import select_col_titles_and_names, select_csvw_dsd_qube_components, select_observation_value_column_title_and_about_url, select_unit_col_about_value_urls 

@dataclass
class DataCubeState:
    cube_shape: CubeShape
    rdf_graph: rdflib.Graph
    dsd_uri: DSDLabelURIResult
    json_path: Path

    """
    Private utility functions.
    """
    def _get_value_for_key(self, key: str, dict: Dict) -> Any:
        maybe_value = dict.get(key)
        if maybe_value is None:
            raise ValueError(f"Could not find the definition for key '{key}'")
        return maybe_value


    """
    Private cached properties.
    """
    @cached_property
    def _unit_col_about_value_urls(self) -> Dict[str, List[UnitColumnAboutValueUrlResult]]:
        """
        Queries and caches unit column about and value urls.
        """
        results = select_unit_col_about_value_urls(self.rdf_graph)
        assert len(results) > 0
        val = {results[0].csv_url:results}
        return val

    @cached_property
    def _obs_val_col_titles_about_urls(self) -> Dict[str, List[ObservationValueColumnTitleAboutUrlResult]]:
        """
        Queries and caches observation value column titles and about urls.
        """
        results = select_observation_value_column_title_and_about_url(self.rdf_graph)
        assert len(results) > 0
        return {results[0].csv_url:results}

    @cached_property
    def _col_names_col_titles(self) -> Dict[str, List[ColTitlesAndNamesResult]]:
        """
        Queries and caches column names and titles.
        """
        results = select_col_titles_and_names(self.rdf_graph)
        assert len(results) > 0
        return {results[0].csv_url:results}

    @cached_property
    def _dsd_qube_components(self) -> Dict[str, List[QubeComponentsResult]]:
        """
        Queries and caches qube components
        """
        results = select_csvw_dsd_qube_components(self.cube_shape, self.rdf_graph, self.dsd_uri, self.json_path)
        assert len(results) > 0
        return {results[0].csv_url: results}


    """
    Public getters for the cached properties.
    """
    def get_unit_col_about_value_urls_for_csv(self, csv_url: str) -> List[UnitColumnAboutValueUrlResult]:
        """
        Getter for _unit_col_about_value_urls cached property.
        """
        value: List[UnitColumnAboutValueUrlResult] = self._get_value_for_key(csv_url, self._unit_col_about_value_urls)
        return value

    def get_obs_val_col_titles_about_urls_for_csv(self, csv_url: str) -> List[ObservationValueColumnTitleAboutUrlResult]:
        """
        Getter for _obs_val_col_titles_about_urls cached property.
        """
        value: List[ObservationValueColumnTitleAboutUrlResult] = self._get_value_for_key(csv_url, self._obs_val_col_titles_about_urls)
        return value

    def get_col_name_col_title_for_csv(self, csv_url: str) -> List[ColTitlesAndNamesResult]:
        """
        Getter for _col_names_col_titles cached property.
        """
        value: List[ColTitlesAndNamesResult] = self._get_value_for_key(csv_url, self._col_names_col_titles)
        return value
    
    def get_dsd_qube_components(self, csv_url: str) -> List[QubeComponentsResult]:
        """
        Getter for DSD Qube Components cached property
        """
        value: List[QubeComponentsResult] = self._get_value_for_key(csv_url, self._dsd_qube_components)
        return value