from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Dict, List, Any

import rdflib


from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.utils.iterables import group_by
from csvcubed.models.sparqlresults import (
    ColTitlesAndNamesResult,
    DataSetDsdUriCsvUrlResult,
    ObservationValueColumnTitleAboutUrlResult,
    QubeComponentResult,
    QubeComponentsResult,
    UnitColumnAboutValueUrlResult,
)
from csvcubed.utils.sparql_handler.sparqlquerymanager import (
    select_col_titles_and_names,
    select_csvw_dsd_qube_components,
    select_data_set_dsd_and_csv_url,
    select_observation_value_column_title_and_about_url,
    select_unit_col_about_value_urls,
)


@dataclass
class DataCubeState:
    rdf_graph: rdflib.ConjunctiveGraph
    cube_shape: CubeShape
    csvw_json_path: Path

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
        return group_by(results, lambda r: r.csv_url)

    @cached_property
    def _obs_val_col_titles_about_urls(
        self,
    ) -> Dict[str, List[ObservationValueColumnTitleAboutUrlResult]]:
        """
        Queries and caches observation value column titles and about urls.
        """
        results = select_observation_value_column_title_and_about_url(self.rdf_graph)
        return group_by(results, lambda r: r.csv_url)

    @cached_property
    def _col_names_col_titles(self) -> Dict[str, List[ColTitlesAndNamesResult]]:
        """
        Queries and caches column names and titles.
        """
        results = select_col_titles_and_names(self.rdf_graph)
        return group_by(results, lambda r: r.csv_url)

    @cached_property
    def _data_set_dsd_and_csv_url(self) -> Dict[str, DataSetDsdUriCsvUrlResult]:
        """
        TODO: Add Description

        """
        results = select_data_set_dsd_and_csv_url(self.rdf_graph)
        results_dict: Dict[str, DataSetDsdUriCsvUrlResult] = {}
        for result in results:
            results_dict[result.csv_url] = result
        return results_dict

    @cached_property
    def _dsd_qube_components(self) -> Dict[str, List[QubeComponentResult]]:
        """
        Queries and caches qube components
        """
        result = select_csvw_dsd_qube_components(
            self.cube_shape, self.rdf_graph, self.csvw_json_path
        )
        return group_by(result.qube_components, lambda c: c.dsd_uri)

    """
    Public getters for the cached properties.
    """

    def get_unit_col_about_value_urls_for_csv(
        self, csv_url: str
    ) -> List[UnitColumnAboutValueUrlResult]:
        """
        Getter for _unit_col_about_value_urls cached property.
        """
        result: List[UnitColumnAboutValueUrlResult] = self._get_value_for_key(
            csv_url, self._unit_col_about_value_urls
        )
        return result

    def get_obs_val_col_titles_about_urls_for_csv(
        self, csv_url: str
    ) -> List[ObservationValueColumnTitleAboutUrlResult]:
        """
        Getter for _obs_val_col_titles_about_urls cached property.
        """
        result: List[
            ObservationValueColumnTitleAboutUrlResult
        ] = self._get_value_for_key(csv_url, self._obs_val_col_titles_about_urls)
        return result

    def get_col_name_col_title_for_csv(
        self, csv_url: str
    ) -> List[ColTitlesAndNamesResult]:
        """
        Getter for _col_names_col_titles cached property.
        """
        result: List[ColTitlesAndNamesResult] = self._get_value_for_key(
            csv_url, self._col_names_col_titles
        )
        return result

    def get_data_set_dsd_urls_for_csv_url(self, csv_url) -> DataSetDsdUriCsvUrlResult:
        """
        Getter for data_set_dsd_and_csv_url_for_csv_url cached property.
        """
        result: DataSetDsdUriCsvUrlResult = self._get_value_for_key(
            csv_url, self._data_set_dsd_and_csv_url
        )
        return result

    def get_dsd_qube_components_for_csv(self, csv_url: str) -> QubeComponentsResult:
        """
        Getter for DSD Qube Components cached property.
        """
        dsd_uri = self.get_data_set_dsd_urls_for_csv_url(csv_url).dsd_uri

        components: List[QubeComponentResult] = self._get_value_for_key(
            dsd_uri, self._dsd_qube_components
        )
        return QubeComponentsResult(components, len(components))
