"""
Inspect Dataframe query results
-------------------------------
"""

from os import linesep
from typing import Optional
import pandas as pd
from dataclasses import dataclass

from treelib import Tree

from csvcubed.cli.inspect.metadatainputvalidator import CSVWType
from csvcubed.utils.printable import get_printable_tabuler_str_from_dataframe
from csvcubed.utils.sparql_handler.sparqlmanager import CSVWShape

HIERARCHY_TREE_CONCEPTS_LIMIT = 100
DATASET_HEAD_TAIL_LIMIT = 10


@dataclass
class DatasetObservationsInfoResult:
    """
    Model to represent get dataset observation info dataframe operation result.
    """

    csvw_type: CSVWType
    csvw_shape: CSVWShape
    num_of_observations: int
    num_of_duplicates: int
    dataset_head: pd.DataFrame
    dataset_tail: pd.DataFrame

    @property
    def output_str(self) -> str:
        formatted_dataset_head = get_printable_tabuler_str_from_dataframe(
            self.dataset_head
        )
        formatted_dataset_tail = get_printable_tabuler_str_from_dataframe(
            self.dataset_tail
        )
        
        title_of_data_samples: str
        if self.csvw_shape == CSVWShape.Standard:
            title_of_data_samples = "Observations"
        elif self.csvw_shape == CSVWShape.Pivoted:
            title_of_data_samples = "Rows"
        else:
            title_of_data_samples = "Concepts"

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
            get_printable_tabuler_str_from_dataframe(
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
