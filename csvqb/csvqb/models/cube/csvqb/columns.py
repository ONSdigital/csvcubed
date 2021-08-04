"""
Columns with qb Components
--------------------------
"""
from dataclasses import field, dataclass
from typing import Optional, TypeVar, Generic, List

from csvqb.inputs import PandasDataTypes, pandas_input_to_columnar
from .components.datastructuredefinition import ColumnarQbDataStructureDefinition
from csvqb.models.cube.columns import CsvColumn
from ...validationerror import ValidationError

QbColumnarDsdType = TypeVar(
    "QbColumnarDsdType", bound=ColumnarQbDataStructureDefinition, covariant=True
)


@dataclass
class QbColumn(CsvColumn, Generic[QbColumnarDsdType]):
    """
    A CSV column and the qb components it relates to.
    """
    csv_column_title: str
    component: QbColumnarDsdType
    output_uri_template: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return self.component.validate_data(data)
