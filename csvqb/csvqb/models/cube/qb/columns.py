"""
Columns with qb Components
--------------------------
"""
from dataclasses import field, dataclass
from typing import Optional, TypeVar, Generic, List

from csvqb.inputs import PandasDataTypes, pandas_input_to_columnar
from csvqb.utils.uri import csvw_column_name_safe
from .components.datastructuredefinition import ColumnarQbDataStructureDefinition
from csvqb.models.cube.columns import CsvColumn
from ...validationerror import ValidationError

QbColumnarDsdType = TypeVar(
    "QbColumnarDsdType", bound=ColumnarQbDataStructureDefinition, covariant=True
)
"""
An instance of a class which inherits from :obj:`~.components.datastructuredefinition.ColumnarQbDataStructureDefinition`.
"""


@dataclass
class QbColumn(CsvColumn, Generic[QbColumnarDsdType]):
    """
    A CSV column and the qb component it relates to.
    """

    csv_column_title: str
    component: QbColumnarDsdType
    csv_column_uri_template: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        # n.b. these won't *necessarily* be URIs, it depends on the csv_column_uri_template
        # but it's good enough for us to ensure values match correctly now.
        column_variable_name = csvw_column_name_safe(self.uri_safe_identifier)
        csv_column_uri_template = (
            self.csv_column_uri_template or "{+" + column_variable_name + "}"
        )
        columnar_data = pandas_input_to_columnar(data, False)
        assert columnar_data is not None

        return self.component.validate_data(
            columnar_data, column_variable_name, csv_column_uri_template
        )
