from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Optional, TypeVar

from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import (
    ColumnDefinition,
    CubeTableIdentifiers,
    IsPivotedShapeMeasureResult,
    QubeComponentsResult,
    UnitResult,
)
from csvcubed.utils.iterables import first, group_by
from csvcubed.utils.sparql_handler.csvw_state import CsvWState
from csvcubed.utils.sparql_handler.sparqlquerymanager import (
    select_column_definitions,
    select_csvw_dsd_qube_components,
    select_data_set_dsd_and_csv_url,
    select_is_pivoted_shape_for_measures_in_data_set,
    select_units,
)

T = TypeVar("T")


@dataclass
class DataCubeState:
    csvw_state: CsvWState

    """
    Private utility functions.
    """

    def _get_value_for_key(self, key: str, dict: Dict[str, T]) -> T:
        maybe_value = dict.get(key)
        if maybe_value is None:
            raise KeyError(f"Could not find the definition for key '{key}'")
        return maybe_value

    """
    Private cached properties.
    """

    @cached_property
    def _column_definitions(self) -> Dict[str, List[ColumnDefinition]]:
        """
        Map of csv_url to the list of column definitions for the given CSV file.
        """
        results = select_column_definitions(self.csvw_state.rdf_graph)
        return group_by(results, lambda r: r.csv_url)

    @cached_property
    def _units(self) -> Dict[str, UnitResult]:
        """ """
        results = select_units(self.csvw_state.rdf_graph)
        return {result.unit_uri: result for result in results}

    @cached_property
    def _cube_table_identifiers(self) -> Dict[str, CubeTableIdentifiers]:
        """
        Identifiers linking a given qb:DataSet with a csvw table (identified by the csvw:url).

        Maps from csv_url to the identifiers.
        """
        results = select_data_set_dsd_and_csv_url(self.csvw_state.rdf_graph)
        results_dict: Dict[str, CubeTableIdentifiers] = {}
        for result in results:
            results_dict[result.csv_url] = result
        return results_dict

    @cached_property
    def _dsd_qube_components(self) -> Dict[str, QubeComponentsResult]:
        """
        Maps csv_url to the qb:DataStructureDefinition components associated with it.
        """
        map_dsd_uri_to_csv_url = {
            i.dsd_uri: i.csv_url for i in self._cube_table_identifiers.values()
        }

        return select_csvw_dsd_qube_components(
            self.csvw_state.rdf_graph,
            self.csvw_state.csvw_json_path,
            map_dsd_uri_to_csv_url,
            self._column_definitions,
        )

    @cached_property
    def _cube_shapes(self) -> Dict[str, CubeShape]:
        """
        A mapping of csvUrl to the given CubeShape. CSV tables which aren't cubes are not present here.
        """

        def _detect_shape_for_cube(
            measures_with_shape: List[IsPivotedShapeMeasureResult],
        ) -> CubeShape:
            """
            Given a metadata validator as input, returns the shape of the cube that metadata describes (Pivoted or
            Standard).
            """
            all_pivoted = True
            all_standard_shape = True
            for measure in measures_with_shape:
                all_pivoted = all_pivoted and measure.is_pivoted_shape
                all_standard_shape = all_standard_shape and not measure.is_pivoted_shape

            if all_pivoted:
                return CubeShape.Pivoted
            elif all_standard_shape:
                return CubeShape.Standard
            else:
                raise TypeError(
                    "The input metadata is invalid as the shape of the cube it represents is not supported. More "
                    "specifically, the input contains some observation values that are pivoted and some are not "
                    "pivoted."
                )

        results = select_is_pivoted_shape_for_measures_in_data_set(
            self.csvw_state.rdf_graph, list(self._cube_table_identifiers.values())
        )

        map_csv_url_to_measure_shape = group_by(results, lambda r: r.csv_url)

        return {
            csv_url: _detect_shape_for_cube(measures_with_shape)
            for (csv_url, measures_with_shape) in map_csv_url_to_measure_shape.items()
        }

    """
    Public getters for the cached properties.
    """

    def get_column_definitions_for_csv(self, csv_url: str) -> List[ColumnDefinition]:
        """
        Getter for _col_names_col_titles cached property.
        """
        result: List[ColumnDefinition] = self._get_value_for_key(
            csv_url, self._column_definitions
        )
        return result

    def get_unit_for_uri(self, uri: str) -> Optional[UnitResult]:
        """ """
        return self._units.get(uri)

    def get_units(self) -> List[UnitResult]:
        """ """
        return list(self._units.values())

    def get_cube_identifiers_for_csv(self, csv_url: str) -> CubeTableIdentifiers:
        """
        Getter for data_set_dsd_and_csv_url_for_csv_url cached property.
        """
        result: CubeTableIdentifiers = self._get_value_for_key(
            csv_url, self._cube_table_identifiers
        )
        return result

    def get_cube_identifiers_for_data_set(
        self, data_set_uri: str
    ) -> CubeTableIdentifiers:
        """
        Getter for data_set_dsd_and_csv_url_for_csv_url cached property.
        """
        result = first(
            self._cube_table_identifiers.values(),
            lambda i: i.data_set_url == data_set_uri,
        )
        if result is None:
            raise KeyError(f"Could not find the data_set with URI '{data_set_uri}'.")

        return result

    def get_dsd_qube_components_for_csv(self, csv_url: str) -> QubeComponentsResult:
        """
        Getter for DSD Qube Components cached property.
        """
        return self._get_value_for_key(csv_url, self._dsd_qube_components)

    def get_shape_for_csv(self, csv_url: str) -> CubeShape:
        return self._get_value_for_key(csv_url, self._cube_shapes)
