from typing import List

from csvcubed.models.cube.cube import Cube
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.cube.qb.components import (
    ExistingQbDimension,
    QbAttribute,
    QbAttributeLiteral,
    QbDimension,
)
from csvcubed.models.cube.qb.validationerrors import (
    CsvColumnLiteralWithUriTemplate,
    CsvColumnUriTemplateMissingError,
    NoDimensionsDefinedError,
)
from csvcubed.models.validationerror import ValidationError
from csvcubed.utils.qb.validation.observations import validate_observations


def validate_qb_component_constraints(cube: Cube) -> List[ValidationError]:
    """
    Validate a :class:`QbCube` to highlight errors in configuration.

    :return: A list of :class:`ValidationError <csvcubed.models.validationerror.ValidationError>` s.
    """

    errors = _validate_dimensions(cube)
    errors += _validate_attributes(cube)
    errors += validate_observations(cube)

    return errors


def _validate_dimensions(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []
    dimension_columns = cube.get_columns_of_dsd_type(QbDimension)

    for c in cube.columns:
        if isinstance(c, QbColumn) and isinstance(
            c.structural_definition, ExistingQbDimension
        ):
            if c.csv_column_uri_template is None:
                errors.append(
                    CsvColumnUriTemplateMissingError(
                        c.csv_column_title, ExistingQbDimension
                    )
                )

    if len(dimension_columns) == 0:
        errors.append(NoDimensionsDefinedError())
    return errors


def _validate_attributes(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []

    for c in cube.columns:
        if isinstance(c, QbColumn) and isinstance(c.structural_definition, QbAttribute):
            if isinstance(c.structural_definition, QbAttributeLiteral):
                if c.csv_column_uri_template is not None:
                    errors.append(
                        CsvColumnLiteralWithUriTemplate(
                            c.csv_column_title,
                            f"{c.structural_definition.__class__.__name__} "
                            + "cannot have a uri_tempate as it holds literal values",
                        )
                    )
            else:
                # Not a QbAttributeLiteral
                if (
                    c.csv_column_uri_template is None
                    and len(c.structural_definition.new_attribute_values) == 0  # type: ignore
                ):
                    errors.append(
                        CsvColumnUriTemplateMissingError(
                            c.csv_column_title,
                            f"{c.structural_definition.__class__.__name__} using existing attribute values",
                        )
                    )

    return errors
