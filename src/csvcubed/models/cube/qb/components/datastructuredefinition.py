"""
Data Structure Definitions
--------------------------

Provides the structure or mapping to components of an RDF Cube (i.e. `qb:DataStructureDefintion`)
"""
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd

from csvcubed.models.pydanticmodel import PydanticModel
from csvcubed.models.validationerror import ValidationError


@dataclass
class QbStructuralDefinition(PydanticModel, ABC):
    """
    Base class for entities holding information necessary to generate one or many qb DataStructureDefinition (DSD)
    components.
    """

    pass


@dataclass
class QbColumnStructuralDefinition(QbStructuralDefinition, ABC):
    """
    Base class representing Qb Data Structure Definitions which can be directly attached to a `pd.DataFrame` column.
    """

    @abstractmethod
    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: Optional[str],
        column_csv_title: str,
    ) -> List[ValidationError]:
        """Validate a columns of data against this component's definition."""
        pass


@dataclass
class SecondaryQbStructuralDefinition(QbStructuralDefinition, ABC):
    """
    Base class representing part of the qb Data Structure Definition which cannot in itself represent a column of data.
    """
