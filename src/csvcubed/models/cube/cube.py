"""
Cube
----
"""
import logging
from dataclasses import dataclass, field
from typing import Generic, Iterable, List, Optional, Set, Tuple, Type, TypeVar

import pandas as pd
import uritemplate

from csvcubed.definitions import URI_TEMPLATE_SPECIAL_PROPERTIES
from csvcubed.models.cube.catalog import CatalogMetadataBase
from csvcubed.models.cube.columns import CsvColumn
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.cube.validationerrors import (
    ColumnNotFoundInDataError,
    ColumnValidationError,
    DuplicateColumnTitleError,
    MissingColumnDefinitionError,
    UriTemplateNameError,
)
from csvcubed.models.pydanticmodel import PydanticModel
from csvcubed.models.validationerror import ValidationError
from csvcubed.utils.log import log_exception
from csvcubed.utils.uri import csvw_column_name_safe

from .qb.catalog import CatalogMetadata
from .qb.components.datastructuredefinition import QbColumnStructuralDefinition
from .qb.components.observedvalue import QbObservationValue
from .uristyle import URIStyle

_logger = logging.getLogger(__name__)

TMetadata = TypeVar("TMetadata", bound=CatalogMetadataBase, covariant=True)

QbColumnarDsdType = TypeVar("QbColumnarDsdType", bound=QbColumnStructuralDefinition)
"""Anything which inherits from :class:`ColumnarQbDataStructureDefinition 
    <csvcubed.models.cube.qb.components.datastructuredefinition.ColumnarQbDataStructureDefinition>`."""


@dataclass
class Cube(Generic[TMetadata], PydanticModel):
    metadata: TMetadata
    data: Optional[pd.DataFrame] = field(default=None, repr=False)
    columns: List[CsvColumn] = field(default_factory=lambda: [], repr=False)
    uri_style: URIStyle = URIStyle.Standard

    @property
    def is_pivoted_shape(self) -> bool:
        obs_val_columns = self.get_columns_of_dsd_type(QbObservationValue)

        all_pivoted = True
        all_standard_shape = True
        for obs_val_col in obs_val_columns:
            all_pivoted = (
                all_pivoted
                and obs_val_col.structural_definition.is_pivoted_shape_observation
            )
            all_standard_shape = (
                all_standard_shape
                and not obs_val_col.structural_definition.is_pivoted_shape_observation
            )

        if all_pivoted:
            return True
        elif all_standard_shape:
            return False
        else:
            raise TypeError("The cube cannot be in both standard and pivoted shape")

    def validate(self) -> List[ValidationError]:
        errors: List[ValidationError] = []
        try:
            errors += self.pydantic_validation()
            errors += self._validate_columns()
        except Exception as e:
            log_exception(_logger, e)
            errors.append(ValidationError(str(e)))
            errors.append(
                ValidationError("An error occurred and validation Failed to Complete")
            )

        return errors

    def get_columns_of_dsd_type(
        self, t: Type[QbColumnarDsdType]
    ) -> List[QbColumn[QbColumnarDsdType]]:
        """
        e.g. `cube.get_columns_of_dsd_type(QbDimension)`

        :return: The :class:`QbColumn <csvcubed.models.cube.qb.columns.QbColumn>` s in :obj:`cube` which have
            :attr:`components` of the requested type :obj:`t`.
        """
        columns_of_type = [
            c
            for c in self.columns
            if isinstance(c, QbColumn) and isinstance(c.structural_definition, t)
        ]

        _logger.debug("Found columns of type %s: %s", t, columns_of_type)

        return columns_of_type

    @staticmethod
    def _get_validation_error_for_exception_in_col(
        csv_column_title: str, error: Exception
    ) -> ColumnValidationError:
        log_exception(_logger, error)
        return ColumnValidationError(csv_column_title, error)

    def _validate_columns(self) -> List[ValidationError]:
        errors: List[ValidationError] = []
        existing_col_titles: Set[str] = set()
        for col in self.columns:
            try:
                if col.csv_column_title in existing_col_titles:
                    errors.append(DuplicateColumnTitleError(col.csv_column_title))
                else:
                    existing_col_titles.add(col.csv_column_title)

                maybe_column_data = None
                if self.data is not None:
                    if col.csv_column_title in self.data.columns:
                        maybe_column_data = self.data[col.csv_column_title]
                    else:
                        errors.append(ColumnNotFoundInDataError(col.csv_column_title))

                if maybe_column_data is not None:
                    errors += col.validate_data(maybe_column_data)
            except Exception as e:
                errors.append(
                    self._get_validation_error_for_exception_in_col(
                        col.csv_column_title, e
                    )
                )

        if self.data is not None:
            defined_column_titles = [c.csv_column_title for c in self.columns]
            for column in list(self.data.columns):
                try:
                    column = str(column)
                    if column not in defined_column_titles:
                        errors.append(MissingColumnDefinitionError(column))
                except Exception as e:
                    errors.append(
                        self._get_validation_error_for_exception_in_col(column, e)
                    )

        # Check for uri template naming errors
        safe_column_names = [
            csvw_column_name_safe(c.uri_safe_identifier) for c in self.columns
        ]
        for uri_template, names in self._csv_column_uri_templates_to_names():
            defined_names = safe_column_names + URI_TEMPLATE_SPECIAL_PROPERTIES
            for name in names:
                if name not in defined_names:
                    _logger.debug(
                        "Unable to find name %s in %s", name, safe_column_names
                    )
                    errors.append(UriTemplateNameError(safe_column_names, uri_template))

        return errors

    def _csv_column_uri_templates_to_names(self) -> Iterable[Tuple]:
        """
        Generates tuples of any configured and not None csv column
        uri templates within the cube, along with the column name
        specified within it.

        Example:
        A cube containing just the following csv column uri templates

        "http://example.com/dimensions/{+foo}"
        "http://example.com/dimensions/{bar}#things"

        yields:
        - "http://example.com/dimensions/{+foo}": "foo",
        then
        - "http://example.com/dimensions/{bar}#things": "bar"
        """

        csv_column_uri_templates = [
            c.csv_column_uri_template for c in self.columns if isinstance(c, QbColumn)
        ]

        template_to_name_map = {
            c: uritemplate.variables(c) for c in csv_column_uri_templates if c
        }

        return template_to_name_map.items()


QbCube = Cube[CatalogMetadata]
