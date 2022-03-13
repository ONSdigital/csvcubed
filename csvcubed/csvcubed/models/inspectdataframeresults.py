"""
Inspect Dataframe query results
-------------------------------
"""

from os import linesep
from pandas import DataFrame
from dataclasses import dataclass

from csvcubed.utils.printable import get_printable_tabuler_str_from_dataframe


@dataclass()
class DatasetObservationsInfoResult:
    """
    Model to represent get dataset observation info dataframe operation result.
    """

    num_of_observations: int
    num_of_duplicates: int
    dataset_head: DataFrame
    dataset_tail: DataFrame

    @property
    def output_str(self) -> str:
        formatted_dataset_head = get_printable_tabuler_str_from_dataframe(
            self.dataset_head
        )
        formatted_dataset_tail = get_printable_tabuler_str_from_dataframe(
            self.dataset_tail
        )
        return f"{linesep}\t- Number of Observations: {self.num_of_observations}{linesep}\t- Number of Duplicates: {self.num_of_duplicates}{linesep}\t- First 10 Observations:{linesep}{formatted_dataset_head}{linesep}{linesep}\t- Last 10 Observations:{linesep}{formatted_dataset_tail}{linesep}"


@dataclass()
class DatasetObservationsByMeasureUnitInfoResult:
    """
    Model to represent get value counts of dataset observations broken-down by measure and unit.
    """

    by_measure_and_unit_val_counts_df: DataFrame

    @property
    def output_str(self) -> str:
        formatted_by_measure_and_unit_val_counts = (
            get_printable_tabuler_str_from_dataframe(
                self.by_measure_and_unit_val_counts_df,
                column_names=["Measure", "Unit", "Count"],
            )
        )
        return f"{linesep}\t- Value counts broken-down by measure and unit (of measure):{linesep}{formatted_by_measure_and_unit_val_counts}"
