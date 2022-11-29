from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Any

import rdflib

from csvcubed.models.sparqlresults import ColTitlesAndNamesResult, ObservationValueColumnTitleAboutUrlResult, QubeComponentResult, UnitColumnAboutValueUrlResult
from csvcubed.utils.sparql_handler.sparqlmanager import select_col_titles_and_names, select_observation_value_column_title_and_about_url, select_unit_col_about_value_urls 

@dataclass
class DataCubeState:
    rdf_graph: rdflib.Graph

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
    def _obs_val_col_title_about_url(self) -> Dict[str, List[ObservationValueColumnTitleAboutUrlResult]]:
        """
        Queries and caches observation value column titles and about urls.
        """
        results = select_observation_value_column_title_and_about_url(self.rdf_graph)
        assert len(results) > 0
        return {results[0].csv_url:results}

    @cached_property
    def _col_name_col_title(self) -> Dict[str, List[ColTitlesAndNamesResult]]:
        """
        Queries and caches column names and titles.
        """
        results = select_col_titles_and_names(self.rdf_graph)
        assert len(results) > 0
        return {results[0].csv_url:results}


    """
    Public getters for the cached properties.
    """
    def get_unit_col_about_value_urls_for_csv(self, csv_url: str) -> List[UnitColumnAboutValueUrlResult]:
        """
        Getter for _unit_col_about_value_urls cached property.
        """
        value: List[UnitColumnAboutValueUrlResult] = self._get_value_for_key(csv_url, self._unit_col_about_value_urls)
        return value

    def get_obs_val_col_title_about_url_for_csv(self, csv_url: str) -> List[ObservationValueColumnTitleAboutUrlResult]:
        """
        Getter for _obs_val_col_title_about_url cached property.
        """
        value: List[ObservationValueColumnTitleAboutUrlResult] = self._get_value_for_key(csv_url, self._obs_val_col_title_about_url)
        return value

    def get_col_name_col_title_for_csv(self, csv_url: str) -> List[ColTitlesAndNamesResult]:
        """
        Getter for _col_name_col_title cached property.
        """
        value: List[ColTitlesAndNamesResult] = self._get_value_for_key(csv_url, self._col_name_col_title)
        return value