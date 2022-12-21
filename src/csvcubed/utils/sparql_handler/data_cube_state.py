from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Any

import rdflib

from csvcubed.models.sparqlresults import (
    ColTitlesAndNamesResult,
    ObservationValueColumnTitleAboutUrlResult,
    UnitColumnAboutValueUrlResult,
    UnitResult,
)
from csvcubed.utils.sparql_handler.sparqlmanager import (
    select_col_titles_and_names,
    select_observation_value_column_title_and_about_url,
    select_unit_col_about_value_urls,
    select_units,
)


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
    def _unit_col_about_value_urls(
        self,
    ) -> Dict[str, List[UnitColumnAboutValueUrlResult]]:
        """
        Queries and caches unit column about and value urls.
        """
        results = select_unit_col_about_value_urls(self.rdf_graph)
        assert len(results) > 0
        val = {results[0].csv_url: results}
        return val

    @cached_property
    def _obs_val_col_titles_about_urls(
        self,
    ) -> Dict[str, List[ObservationValueColumnTitleAboutUrlResult]]:
        """
        Queries and caches observation value column titles and about urls.
        """
        results = select_observation_value_column_title_and_about_url(self.rdf_graph)
        assert len(results) > 0
        return {results[0].csv_url: results}

    @cached_property
    def _col_names_col_titles(self) -> Dict[str, List[ColTitlesAndNamesResult]]:
        """
        Queries and caches column names and titles.
        """
        results = select_col_titles_and_names(self.rdf_graph)
        assert len(results) > 0
        return {results[0].csv_url: results}

    @cached_property
    def _units(self) -> Dict[str, UnitResult]:
        """ """
        results = select_units(self.rdf_graph)
        return {result.unit_uri: result for result in results}

    """
    Public getters for the cached properties.
    """

    def get_unit_col_about_value_urls_for_csv(
        self, csv_url: str
    ) -> List[UnitColumnAboutValueUrlResult]:
        """
        Getter for _unit_col_about_value_urls cached property.
        """
        value: List[UnitColumnAboutValueUrlResult] = self._get_value_for_key(
            csv_url, self._unit_col_about_value_urls
        )
        return value

    def get_obs_val_col_titles_about_urls_for_csv(
        self, csv_url: str
    ) -> List[ObservationValueColumnTitleAboutUrlResult]:
        """
        Getter for _obs_val_col_titles_about_urls cached property.
        """
        value: List[
            ObservationValueColumnTitleAboutUrlResult
        ] = self._get_value_for_key(csv_url, self._obs_val_col_titles_about_urls)
        return value

    def get_col_name_col_title_for_csv(
        self, csv_url: str
    ) -> List[ColTitlesAndNamesResult]:
        """
        Getter for _col_names_col_titles cached property.
        """
        value: List[ColTitlesAndNamesResult] = self._get_value_for_key(
            csv_url, self._col_names_col_titles
        )
        return value

    def get_unit_for_uri(self, uri: str) -> UnitResult:
        """ """
        value: UnitResult = self._get_value_for_key(uri, self._units)
        return value

    def get_units(self) -> List[UnitResult]:
        """ """
        return self._units.values()
