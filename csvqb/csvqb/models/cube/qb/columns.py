from typing import Optional, TypeVar, Generic, Set, List
import pandas as pd


from .components.datastructuredefinition import QbDataStructureDefinition
from csvqb.models.validationerror import ValidationError
from csvqb.models.cube.columns import CsvColumn


QbComponentType = TypeVar("QbComponentType", bound=QbDataStructureDefinition)


class QbColumn(CsvColumn, Generic[QbComponentType]):
    """
        A CSV column and the qb components it relates to.
    """

    component: QbComponentType
    """The qb components defined by this column."""
    value_template: Optional[str]
    """The formatted string that maps the raw column value to a CSV-W `propertyUrl`."""

    def __init__(self,
                 csv_column_title: str,
                 component: QbComponentType,
                 value_template: Optional[str] = None,
                 uri_safe_identifier: Optional[str] = None):
        CsvColumn.__init__(self, csv_column_title, uri_safe_identifier)
        self.component = component
        self.csv_column_title = csv_column_title
        self.value_template = value_template

    def validate(self, column_data: Optional[pd.Series]) -> List[ValidationError]:
        errors = self.component.validate()
        if column_data is not None:
            errors += self.component.validate_data(column_data)

        return errors
