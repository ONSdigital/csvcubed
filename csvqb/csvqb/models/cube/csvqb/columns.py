from typing import Optional, TypeVar, Generic, List
import pandas as pd


from .components.datastructuredefinition import ColumnarQbDataStructureDefinition
from csvqb.models.validationerror import ValidationError
from csvqb.models.cube.columns import CsvColumn


QbColumnarDsdType = TypeVar("QbColumnarDsdType", bound=ColumnarQbDataStructureDefinition, covariant=True)


class QbColumn(CsvColumn, Generic[QbColumnarDsdType]):
    """
        A CSV column and the qb components it relates to.
    """

    def __init__(self,
                 csv_column_title: str,
                 component: QbColumnarDsdType,
                 output_uri_template: Optional[str] = None,
                 uri_safe_identifier: Optional[str] = None):
        CsvColumn.__init__(self, csv_column_title, uri_safe_identifier)
        if not isinstance(component, ColumnarQbDataStructureDefinition):
            raise Exception(f"{component} of type {type(component)} is not a valid columnar component.")
        self.component: QbColumnarDsdType = component
        self.output_uri_template: Optional[str] = output_uri_template

    def __str__(self) -> str:
        return f"QbColumn('{self.csv_column_title}', {self.component})"

    def validate(self, column_data: Optional[pd.Series]) -> List[ValidationError]:
        errors = self.component.validate()
        if column_data is not None:
            errors += self.component.validate_data(column_data)

        return errors
