"""
Data Structure Definitions
--------------------------
"""
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd

from csvcubed.models.pydanticmodel import PydanticModel
from csvcubed.models.validationerror import ValidationError


@dataclass
class QbDataStructureDefinition(PydanticModel, ABC):
    """
    Base class for entities holding information necessary to generate one or many qb DataStructureDefinition (DSD)
    components.
    """

    pass


@dataclass
class ColumnarQbDataStructureDefinition(QbDataStructureDefinition, ABC):
    """
    Base class representing Qb Data Structure Definitions which can be directly attached to a `pd.DataFrame` column.
    """

    @abstractmethod
    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: Optional[str],
    ) -> List[ValidationError]:
        """Validate a columns of data against this component's definition."""
        pass


@dataclass
class MultiQbDataStructureDefinition(ColumnarQbDataStructureDefinition, ABC):
    """
    Base class representing an entity which defines a group of `QbDataStructureDefinition` s.
    """
