"""
Data Structure Definitions
--------------------------
"""
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List

from csvqb.inputs import PandasDataTypes
from csvqb.models.pydanticmodel import PydanticModel
from csvqb.models.validationerror import ValidationError


@dataclass
class QbDataStructureDefinition(PydanticModel, ABC):
    """
    Base class for entities holding information necessary to generate one or many qb DataStructureDefinition (DSD)
    components.
    """

    @abstractmethod
    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        """Validate some data against this component's definition."""
        pass


@dataclass
class ColumnarQbDataStructureDefinition(QbDataStructureDefinition, ABC):
    """
    Base class representing Qb Data Structure Definitions which can be directly attached to a `pd.DataFrame` column.
    """

    pass


@dataclass
class MultiQbDataStructureDefinition(ColumnarQbDataStructureDefinition, ABC):
    """
    Base class representing an entity which defines a group of `QbDataStructureDefinition` s.
    """
