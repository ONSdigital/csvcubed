"""
Mapping
-------

Map info.json v1.* definitions to QB column components
"""
import copy
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union

import csvcubed.readers.cubeconfig.v1.columnschema as schema
from csvcubed.inputs import PandasDataTypes
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.cube.qb.components.codelist import CompositeQbCodeList
from csvcubed.models.jsonvalidationerrors import JsonSchemaValidationError

_logger = logging.getLogger(__name__)


def map_column_to_qb_component(
    column_title: str,
    column: dict,
    data: PandasDataTypes,
    cube_config_minor_version: Optional[int],
    config_path: Optional[Path] = None,
) -> Tuple[QbColumn, List[JsonSchemaValidationError]]:
    """
    Takes a config.json v1.* column mapping and, if valid,
    returns a :obj:`~csvcubed.models.cube.qb.columns.QbColumn`.
    """
    schema_mapping = _from_column_dict_to_schema_model(column_title, column)

    if isinstance(schema_mapping, schema.NewDimension):
        _logger.debug(f"Identified {schema_mapping.as_dict()} as NewDimension")
        (
            structural_definition,
            code_list_schema_validation_errors,
        ) = schema_mapping.map_to_new_qb_dimension(
            column_title,
            data,
            cube_config_minor_version,
            config_path=config_path,
        )

        # If the code list is a CompositeQbCodeList, the uri template needs to be reset to point at the newly
        # created composite code list
        cell_uri_template = (
            None
            if isinstance(structural_definition.code_list, CompositeQbCodeList)
            else schema_mapping.cell_uri_template
        )

        return (
            QbColumn(
                column_title,
                structural_definition,
                csv_column_uri_template=cell_uri_template,
            ),
            code_list_schema_validation_errors,
        )

    elif isinstance(schema_mapping, schema.ExistingDimension):
        _logger.debug(f"Identified {schema_mapping.as_dict()} as ExistingDimension")
        return (
            QbColumn(
                column_title,
                schema_mapping.map_to_existing_qb_dimension(),
                csv_column_uri_template=schema_mapping.cell_uri_template,
            ),
            [],
        )

    elif isinstance(schema_mapping, schema.NewAttributeLiteral):
        _logger.debug(f"Identified {schema_mapping.as_dict()} as NewAttributeLiteral")
        return (
            QbColumn(
                column_title,
                schema_mapping.map_to_new_qb_attribute(column_title),
            ),
            [],
        )

    elif isinstance(schema_mapping, schema.NewAttributeResource):
        _logger.debug(f"Identified {schema_mapping.as_dict()} as NewAttributeResource")
        return (
            QbColumn(
                column_title,
                schema_mapping.map_to_new_qb_attribute(column_title, data),
                csv_column_uri_template=schema_mapping.cell_uri_template,
            ),
            [],
        )

    elif isinstance(schema_mapping, schema.ExistingAttributeLiteral):
        _logger.debug(
            f"Identified {schema_mapping.as_dict()} as ExistingAttributeLiteral"
        )
        return (
            QbColumn(column_title, schema_mapping.map_to_existing_qb_attribute()),
            [],
        )

    elif isinstance(schema_mapping, schema.ExistingAttributeResource):
        _logger.debug(
            f"Identified {schema_mapping.as_dict()} as ExistingAttributeResource"
        )
        return (
            QbColumn(
                column_title,
                schema_mapping.map_to_existing_qb_attribute(data),
                csv_column_uri_template=schema_mapping.cell_uri_template,
            ),
            [],
        )

    elif isinstance(schema_mapping, schema.NewUnits):
        _logger.debug(f"Identified {schema_mapping.as_dict()} as NewUnits")
        return (
            QbColumn(column_title, schema_mapping.map_to_new_qb_multi_units(data)),
            [],
        )

    elif isinstance(schema_mapping, schema.ExistingUnits):
        _logger.debug(f"Identified {schema_mapping.as_dict()} as ExistingUnits")
        return (
            QbColumn(
                column_title,
                schema_mapping.map_to_existing_qb_multi_units(data, column_title),
                csv_column_uri_template=schema_mapping.cell_uri_template,
            ),
            [],
        )

    elif isinstance(schema_mapping, schema.NewMeasures):
        _logger.debug(f"Identified {schema_mapping.as_dict()} as NewMeasures")
        return (
            QbColumn(
                column_title, schema_mapping.map_to_new_multi_measure_dimension(data)
            ),
            [],
        )

    elif isinstance(schema_mapping, schema.ExistingMeasures):
        _logger.debug(f"Identified {schema_mapping.as_dict()} as ExistingMeasures")
        return (
            QbColumn(
                column_title,
                schema_mapping.map_to_existing_multi_measure_dimension(
                    column_title, data
                ),
                csv_column_uri_template=schema_mapping.cell_uri_template,
            ),
            [],
        )

    elif isinstance(schema_mapping, schema.ObservationValue):
        _logger.debug(f"Identified {schema_mapping.as_dict()} as ObservationValue")
        return (QbColumn(column_title, schema_mapping.map_to_qb_observation()), [])

    else:
        raise ValueError(f"Unmatched column type {type(schema_mapping)}")


def _from_column_dict_to_schema_model(
    column_title: str,
    column: dict,
) -> Union[
    schema.NewDimension,
    schema.ExistingDimension,
    schema.NewAttributeLiteral,
    schema.NewAttributeResource,
    schema.ExistingAttributeLiteral,
    schema.ExistingAttributeResource,
    schema.NewUnits,
    schema.ExistingUnits,
    schema.NewMeasures,
    schema.ExistingMeasures,
    schema.ObservationValue,
]:
    """
    N.B. when using the :meth:`dict_fields_match_class` method, we need to ensure that we check for types with
    required properties *before* types without required properties.
    """
    column_type = column.get("type", "dimension")
    column_without_type = copy.deepcopy(column)
    if "type" in column_without_type:
        del column_without_type["type"]

    if column_type == "dimension":
        if schema.ExistingDimension.dict_fields_match_class(column_without_type):
            return schema.ExistingDimension.from_dict(column_without_type)
        elif schema.NewDimension.dict_fields_match_class(column_without_type):
            return schema.NewDimension.from_dict(column_without_type)
        else:
            raise Exception(
                f"Column with config: '{column}' did not match "
                "either New or Existing Dimension using schema"
            )
    elif column_type == "attribute":
        if schema.ExistingAttributeResource.dict_fields_match_class(
            column_without_type
        ):
            return schema.ExistingAttributeResource.from_dict(column_without_type)
        elif schema.ExistingAttributeLiteral.dict_fields_match_class(
            column_without_type
        ):
            return schema.ExistingAttributeLiteral.from_dict(column_without_type)
        elif schema.NewAttributeLiteral.dict_fields_match_class(column_without_type):
            return schema.NewAttributeLiteral.from_dict(column_without_type)
        elif schema.NewAttributeResource.dict_fields_match_class(column_without_type):
            return schema.NewAttributeResource.from_dict(column_without_type)
        else:
            raise Exception(
                f"Column with config '{column}' did not match either New or "
                f"Existing schema as either a Literal or Resource attribute"
            )
    elif column_type == "units":
        if schema.ExistingUnits.dict_fields_match_class(column_without_type):
            return schema.ExistingUnits.from_dict(column_without_type)
        elif schema.NewUnits.dict_fields_match_class(column_without_type):
            return schema.NewUnits.from_dict(column_without_type)
        else:
            raise Exception(
                f"Column with type '{column_type}' did not match either New or "
                f"Existing Units schema"
            )
    elif column_type == "measures":
        if schema.ExistingMeasures.dict_fields_match_class(column_without_type):
            return schema.ExistingMeasures.from_dict(column_without_type)
        elif schema.NewMeasures.dict_fields_match_class(column_without_type):
            return schema.NewMeasures.from_dict(column_without_type)
        else:
            raise Exception(
                f"Column with type '{column_type}' did not match either New or "
                f"Existing Measures schema"
            )
    elif column_type == "observations":
        return schema.ObservationValue.from_dict(column)

    raise ValueError(
        f"Column '{column_title}' with type '{column_type}' could not be understood."
    )
