"""
CSV With Column Definitions
---------------------------
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List

import csvw


@dataclass
class CsvWithColumnDefinitions:
    csv_path: Path
    columns: List[csvw.Column]

    def __init__(self, csv_path: Path, columns: List[csvw.Column]):
        self.csv_path = csv_path
        self.columns = columns

    def __hash__(self):
        return self.csv_path.__hash__()
