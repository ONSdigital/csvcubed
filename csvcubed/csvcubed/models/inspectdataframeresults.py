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


@dataclass
class DatasetObservationsInfoResult:
    """
    Model to represent get dataset observation info dataframe operation result.
    """

    csvw_type: CSVWType
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

        obs_or_concepts_str = (
            "Observations" if self.csvw_type == CSVWType.QbDataSet else "Concepts"
        )
        return f"{linesep}\t- Number of {obs_or_concepts_str}: {self.num_of_observations}{linesep}\t- Number of Duplicates: {self.num_of_duplicates}{linesep}\t- First 10 Observations:{linesep}{formatted_dataset_head}{linesep}{linesep}\t- Last 10 Observations:{linesep}{formatted_dataset_tail}{linesep}"


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
        return f"{linesep}\t- Value counts broken-down by measure and unit (of measure):{linesep}{formatted_by_measure_and_unit_val_counts}"


@dataclass
class CodelistHierarchyInfoResult:
    """
    Model to represent codelist hierarchy (i.e. tree strcuture).
    """

    tree: Tree

    @property
    def output_str(self) -> str:
        return f"{linesep}\t- Hierarchy:{linesep}{self.tree}{linesep}\t- Hierarchy depth: {self.tree.depth()}"
