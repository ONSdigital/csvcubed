"""
Data Cube Inspector
-------------------

Provides access to inspect the contents of an rdflib graph containing
one of more data cubes.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Optional

from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import (
    CodelistsResult,
    CubeTableIdentifiers,
    IsPivotedShapeMeasureResult,
    QubeComponentsResult,
    UnitResult,
)
from csvcubed.utils.dict import get_from_dict_ensure_exists
from csvcubed.utils.iterables import first, group_by
from csvcubed.utils.sparql_handler.csvw_inspector import CsvWInspector
from csvcubed.utils.sparql_handler.sparqlquerymanager import (
    select_csvw_dsd_qube_components,
    select_data_set_dsd_and_csv_url,
    select_dsd_code_list_and_cols,
    select_is_pivoted_shape_for_measures_in_data_set,
    select_units,
)


@dataclass
class DataCubeInspector:
    """Provides access to inspect the data cubes contained in an rdflib graph."""

    csvw_inspector: CsvWInspector

    """
    Private cached properties.
    """

    @cached_property
    def _units(self) -> Dict[str, UnitResult]:
        """
        Gets the unit_uri for each UnitResult
        """
        results = select_units(self.csvw_inspector.rdf_graph)
        return {result.unit_uri: result for result in results}

    @cached_property
    def _cube_table_identifiers(self) -> Dict[str, CubeTableIdentifiers]:
        """
        Identifiers linking a given qb:DataSet with a csvw table (identified by the csvw:url).

        Maps from csv_url to the identifiers.
        """
        results = select_data_set_dsd_and_csv_url(self.csvw_inspector.rdf_graph)
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
            self.csvw_inspector.rdf_graph,
            self.csvw_inspector.csvw_json_path,
            map_dsd_uri_to_csv_url,
            self.csvw_inspector.column_definitions,
        )

    @cached_property
    def _cube_shapes(self) -> Dict[str, CubeShape]:
        """
        A mapping of csvUrl to the given CubeShape. CSV tables which aren't cubes
         are not present here.
        """

        def _detect_shape_for_cube(
            measures_with_shape: List[IsPivotedShapeMeasureResult],
        ) -> CubeShape:
            """
            Given a metadata validator as input, returns the shape of the cube that
             metadata describes (Pivoted or Standard).
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
                    "The input metadata is invalid as the shape of the cube it represents is "
                    "not supported. More specifically, the input contains some observation values "
                    "that are pivoted and some are not pivoted."
                )

        results = select_is_pivoted_shape_for_measures_in_data_set(
            self.csvw_inspector.rdf_graph, list(self._cube_table_identifiers.values())
        )

        map_csv_url_to_measure_shape = group_by(results, lambda r: r.csv_url)

        return {
            csv_url: _detect_shape_for_cube(measures_with_shape)
            for (csv_url, measures_with_shape) in map_csv_url_to_measure_shape.items()
        }

    @cached_property
    def _codelists_and_cols(self) -> Dict[str, CodelistsResult]:
        """
        Maps the csv url to the code lists/columns featured in the CSV.
        """
        return select_dsd_code_list_and_cols(
            self.csvw_inspector.rdf_graph,
            self.csvw_inspector.csvw_json_path,
        )

    """
    Public getters for the cached properties.
    """

    def get_unit_for_uri(self, uri: str) -> Optional[UnitResult]:
        """
        Get a specific unit, by its uri.
        """
        return self._units.get(uri)

    def get_units(self) -> List[UnitResult]:
        """
        Returns all units defined in the graph.
        """
        return list(self._units.values())

    def get_cube_identifiers_for_csv(self, csv_url: str) -> CubeTableIdentifiers:
        """
        Get csv url, data set uri, data set label and DSD uri for the given csv url.
        """
        result: CubeTableIdentifiers = get_from_dict_ensure_exists(
            self._cube_table_identifiers, csv_url
        )
        return result

    def get_cube_identifiers_for_data_set(
        self, data_set_uri: str
    ) -> CubeTableIdentifiers:
        """
        Get csv url, data set uri, data set label and DSD uri for the given data set uri.
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
        Get DSD Qube Components for the given csv url.
        """
        return get_from_dict_ensure_exists(self._dsd_qube_components, csv_url)

    def get_shape_for_csv(self, csv_url: str) -> CubeShape:
        """
        Get the cube shape.
        """
        return get_from_dict_ensure_exists(self._cube_shapes, csv_url)

    def get_code_lists_and_cols(self, csv_url: str) -> CodelistsResult:
        """
        Get the codelists and columns associated with the given csv url.
        """

        return self._codelists_and_cols.get(csv_url, CodelistsResult([], 0))
