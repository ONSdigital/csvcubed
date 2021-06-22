from abc import ABC, abstractmethod
import pandas as pd
from typing import List


class QbComponent(ABC):
    """
        Base class for entities holding information necessary to generate one or many qb DataStructureDefinition (DSD)
        components.
    """

    @abstractmethod
    def validate(self) -> bool:
        """Validate this component's metadata."""
        pass

    @abstractmethod
    def validate_data(self, data: pd.Series) -> bool:
        """Validate some data against this component's definition."""
        pass


class QbMetaComponent(QbComponent, ABC):
    """
        Base class representing an entity which defines a group of `QbComponent`s
    """

    @abstractmethod
    def get_qb_components(self) -> List[QbComponent]:
        pass
