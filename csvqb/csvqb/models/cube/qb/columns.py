from typing import Optional, TypeVar, Generic, Set, List
import pandas as pd


from .components.component import QbComponent

QbComponentType = TypeVar("QbComponentType", bound=QbComponent)


class QbColumn(Generic[QbComponentType]):
    """
        A CSV column and the qb components it relates to.
    """

    component: QbComponentType
    """The qb components defined by this column."""
    value_template: str
    """The formatted string that maps the raw column value to a CSV-W `propertyUrl`."""

    def __init__(self, component: QbComponentType, csv_column_title: str,
                 value_template: Optional[str] = None) -> "QbColumn[QbComponentType]":
        self.component = component
        self.csv_column_title = csv_column_title
        self.value_template = value_template

    def validate(self, column_data: Optional[pd.Series]) -> bool:
        self.component.validate()
        if column_data is not None:
            self.component.validate_data(column_data)
