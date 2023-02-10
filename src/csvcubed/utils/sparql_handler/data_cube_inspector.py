from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Optional, TypeVar

from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import (
    CodelistsResult,
    ColumnDefinition,
    CSVWTableSchemaFileDependenciesResult,
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
    select_csvw_table_schema_file_dependencies,
    select_data_set_dsd_and_csv_url,
    select_dsd_code_list_and_cols,
    select_is_pivoted_shape_for_measures_in_data_set,
    select_units,
)

T = TypeVar("T")


@dataclass
class DataCubeInspector:
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
        """
        Maps the csv url to the unit results of the given CSV.
        """
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

    @cached_property
    def _codelists_and_cols(self) -> Dict[str, CodelistsResult]:
        """
        Maps the csv url to the code lists/columns featured in the CSV.
        """
        return select_dsd_code_list_and_cols(
            self.csvw_state.rdf_graph,
            self.csvw_state.csvw_json_path,
        )

    # @cached_property
    # def _csvw_table_schema_file_dependencies(
    #     self,
    # ) -> Dict[str, CSVWTableSchemaFileDependenciesResult]:
    #     """
    #     Stores the csv url and results of the CSVW's table schema file dependencies.
    #     """
    #     return select_csvw_table_schema_file_dependencies(self.csvw_state.rdf_graph)

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
        """
        Get a specific unit, by its uri.
        """
        return self._units.get(uri)

    def get_units(self) -> List[UnitResult]:
        """
        Get all units in the data cube.
        """
        return list(self._units.values())

    def get_cube_identifiers_for_csv(self, csv_url: str) -> CubeTableIdentifiers:
        """
        Get csv url, data set uri, data set label and DSD uri for the given csv url.
        """
        result: CubeTableIdentifiers = self._get_value_for_key(
            csv_url, self._cube_table_identifiers
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
        return self._get_value_for_key(csv_url, self._dsd_qube_components)

    def get_shape_for_csv(self, csv_url: str) -> CubeShape:
        """
        Get the cube shape.
        """
        return self._get_value_for_key(csv_url, self._cube_shapes)

    def get_code_lists_and_cols(self, csv_url: str) -> CodelistsResult:
        """
        Get the codelists and columns associated with the given csv url.
        """
        return self._get_value_for_key(csv_url, self._codelists_and_cols)

    def get_suppressed_columns_for_csv(self, csv_url: str) -> List[str]:
        """
        Get the suppressed columns from the input csv url's column definitions.
        """
        column_definitions = self.get_column_definitions_for_csv(csv_url)

        result = [
            column_definition.title
            for column_definition in column_definitions
            if column_definition.suppress_output and column_definition.title is not None
        ]

        return result

    # def get_csvw_table_schema_file_dependencies(
    #     self, csv_url: str
    # ) -> CSVWTableSchemaFileDependenciesResult:
    #     """
    #     Getter for the csvw table schema file dependencies cached property.
    #     """
    #     return self._get_value_for_key(
    #         csv_url, self._csvw_table_schema_file_dependencies
    #     )
