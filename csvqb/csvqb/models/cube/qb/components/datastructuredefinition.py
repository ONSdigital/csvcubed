from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Optional, Dict, Any


from csvqb.models.validationerror import ValidationError


class QbDataStructureDefinition(ABC):
    """
        Base class for entities holding information necessary to generate one or many qb DataStructureDefinition (DSD)
        components.
    """

    @abstractmethod
    def validate(self) -> List[ValidationError]:
        """Validate this component's metadata."""
        pass

    @abstractmethod
    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        """Validate some data against this component's definition."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Ensure that descendents implement the to string method to help users debug their data."""
        pass


class ColumnarQbDataStructureDefinition(QbDataStructureDefinition, ABC):
    """
        Base class representing Qb Data Structure Definitions which can be directly attached to a pd.DataFrame column.
    """
    pass


class MultiQbDataStructureDefinition(ColumnarQbDataStructureDefinition, ABC):
    """
        Base class representing an entity which defines a group of `QbDataStructureDefinition`s
    """

    @abstractmethod
    def get_qb_components(self) -> List[QbDataStructureDefinition]:
        pass
