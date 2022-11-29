"""
Inspect Dataframe query results
-------------------------------
"""

from dataclasses import dataclass
from os import linesep
from typing import Optional

import pandas as pd
from treelib import Tree

from csvcubed.models.csvcubedexception import FailedToConvertDataFrameToStringException
from csvcubed.models.csvwtype import CSVWType
from csvcubed.models.cube.cube_shape import CubeShape

HIERARCHY_TREE_CONCEPTS_LIMIT = 100
DATASET_HEAD_TAIL_LIMIT = 10


def _get_printable_tabuler_str_from_dataframe(
    df: pd.DataFrame, column_names=None
) -> str:
    """
    Converts the given dataframe into a printable tabular.

    Member of :file:`./utils/printable`.

    :return: `str` - string representation of the given dataframe
    """
    if column_names:
        df.columns = column_names
    output_str = df.to_string(index=False)
    if output_str:
        return output_str
    raise FailedToConvertDataFrameToStringException()


@dataclass
class DatasetObservationsInfoResult:
    """
    Model to represent get dataset observation info dataframe operation result.
    """

    csvw_type: CSVWType
    cube_shape: Optional[CubeShape]
    num_of_observations: int
    num_of_duplicates: int
    dataset_head: pd.DataFrame
    dataset_tail: pd.DataFrame

    @property
    def output_str(self) -> str:
        formatted_dataset_head = _get_printable_tabuler_str_from_dataframe(
            self.dataset_head
        )
        formatted_dataset_tail = _get_printable_tabuler_str_from_dataframe(
            self.dataset_tail
        )

        title_of_data_samples: str
        if self.cube_shape is None:
            title_of_data_samples = "Concepts"
        elif self.cube_shape == CubeShape.Standard:
            title_of_data_samples = "Observations"
        else:
            title_of_data_samples = "Rows"

        if self.num_of_observations < DATASET_HEAD_TAIL_LIMIT:
            observations_str = (
                f"""- {title_of_data_samples}: {linesep}{formatted_dataset_head}"""
            )
        else:
            observations_str = f"""- First 10 {title_of_data_samples}: {linesep}{formatted_dataset_head}
        - Last 10 {title_of_data_samples}: {linesep}{formatted_dataset_tail}"""

        return f"""
        - Number of {title_of_data_samples}: {self.num_of_observations}
        - Number of Duplicates: {self.num_of_duplicates}
        {observations_str}
        """


@dataclass
class DatasetSingleMeasureResult:
    measure_uri: str
    measure_label: Optional[str]


@dataclass
class DatasetObservationsByMeasureUnitInfoResult:
    """
    Model to represent get value counts of dataset observations broken-down by measure and unit.
    """

    by_measure_and_unit_val_counts_df: pd.DataFrame

    @property
    def output_str(self) -> str:
        formatted_by_measure_and_unit_val_counts = (
            _get_printable_tabuler_str_from_dataframe(
                self.by_measure_and_unit_val_counts_df,
                column_names=["Measure", "Unit", "Count"],
            )
        )
        return f"""
        - Value counts broken-down by measure and unit (of measure):{linesep}{formatted_by_measure_and_unit_val_counts}
        """


@dataclass
class CodelistHierarchyInfoResult:
    """
    Model to represent codelist hierarchy tree.
    """

    tree: Tree

    @property
    def output_str(self) -> str:
        hierarchy_output = (
            f"{linesep}{self.tree}"
            if len(self.tree.all_nodes()) < HIERARCHY_TREE_CONCEPTS_LIMIT
            else " Hierarchy is too large to display."
        )
        return f"""
        - Concepts hierarchy depth: {self.tree.depth()}
        - Concepts hierarchy:{hierarchy_output}
        """
