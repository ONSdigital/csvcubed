"""Output writer for CSV-qb"""
import json
from pathlib import Path
from typing import Optional


from csvqb.models.cube import *


def write_metadata(cube: Cube, output_file: Path) -> None:
    tables = [
        {
            "url": "output.csv",  # todo
            "tableSchema": {
                "columns": [_generate_csvqb_column(c) for c in cube.columns]
            }
        }
    ]

    csvw_metadata = {
        "@context": "http://www.w3.org/ns/csvw",
        "@id": _document_relative_uri("dataset"),
        "tables": tables,
        "rdfs:label": cube.metadata.title,
        "dc:title": cube.metadata.title,
        "rdfs:comment": cube.metadata.summary,
        "dc:description": cube.metadata.description
    }

    with open(output_file, "w+") as f:
        json.dump(csvw_metadata, f, indent=4)


def _document_relative_uri(uri_fragment: str) -> str:
    return f"#{uri_fragment}"


def _generate_csvqb_column(column: CsvColumn) -> dict:
    csvw_col = {
        "titles": column.csv_column_title,
        "name": column.uri_safe_identifier
    }

    if isinstance(column, SuppressedCsvColumn):
        csvw_col["suppressOutput"] = True
    elif isinstance(column, QbColumn):
        _define_csvw_column_for_qb_column(csvw_col, column)
    else:
        raise Exception(f"Unhandled column type ({type(column)}) with title '{column.csv_column_title}'")

    return csvw_col


def _define_csvw_column_for_qb_column(csvw_col: dict, column: QbColumn) -> None:
    (property_url, default_value_url) = _get_default_property_value_uris_for_column(column)
    if property_url is not None:
        csvw_col["propertyUrl"] = property_url

    if column.output_uri_template is not None:
        # User-specified value overrides our default guess.
        csvw_col["valueUrl"] = column.output_uri_template
    elif default_value_url is not None:
        csvw_col["valueUrl"] = default_value_url

    if isinstance(column.component, QbObservationValue):
        csvw_col["datatype"] = column.component.data_type


def _get_default_property_value_uris_for_column(column: QbColumn) -> \
        (Optional[str], Optional[str]):
    if isinstance(column.component, QbDimension):
        return _get_default_property_value_uris_for_dimension(column)
    elif isinstance(column.component, QbAttribute):
        return _get_default_property_value_uris_for_attribute(column)
    elif isinstance(column.component, QbMultiUnits):
        # todo: How do we deal with the situation where the user wants to specify a mixture of local
        # and remote units in the same column?
        local_unit_value_uri = _document_relative_uri(f"unit/{_get_column_uri_template_fragment(column)}")
        return "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure", local_unit_value_uri
    elif isinstance(column.component, QbMultiMeasureDimension):
        # todo: How do we deal with the situation where the user wants to specify a mixture of local
        # and remote measures in the same column?
        local_measure_value_uri = _document_relative_uri(
            f"measure/{_get_column_uri_template_fragment(column)}")
        return "http://purl.org/linked-data/cube#measureType", local_measure_value_uri
    elif isinstance(column.component, QbObservationValue):
        return None, None
    else:
        raise Exception(f"Unhandled component type {type(column.component)}")


def _get_default_property_value_uris_for_dimension(column: QbColumn[QbDimension]) -> (str, str):
    dimension = column.component
    if isinstance(dimension, ExistingQbDimension):
        # todo: If we have an ExistingQbDimension without a `column.output_uri_template` specified, ensure
        #  we get a validation error before getting here. We can't look-up what the code-list's URI template
        #  should look like at this point.
        return dimension.dimension_uri, None
    elif isinstance(dimension, NewQbDimension):
        local_dimension_uri = _document_relative_uri(f"dimension/{dimension.uri_safe_identifier}")
        value_uri = _get_column_uri_template_fragment(column)
        if dimension.code_list is not None:
            value_uri = _get_default_value_uri_for_code_list_concepts(column, dimension.code_list)

        return local_dimension_uri, value_uri
    else:
        raise Exception(f"Unhandled dimension type {type(dimension)}")


def _get_default_property_value_uris_for_attribute(column: QbColumn[QbAttribute]) -> (str, str):
    attribute = column.component
    if isinstance(attribute, ExistingQbAttribute):
        return attribute.attribute_uri, _get_column_uri_template_fragment(column)
    elif isinstance(attribute, NewQbAttribute):
        local_attribute_uri = _document_relative_uri(f"attribute/{attribute.uri_safe_identifier}")
        value_uri = _get_column_uri_template_fragment(column)
        if attribute.code_list is not None:
            value_uri = _get_default_value_uri_for_code_list_concepts(column, attribute.code_list)

        return local_attribute_uri, value_uri

    else:
        raise Exception(f"Unhandled attribute type {type(attribute)}")


def _get_column_uri_template_fragment(column: CsvColumn, escape_value: bool = False) -> str:
    if escape_value:
        return "{" + column.uri_safe_identifier + "}"

    return "{+" + column.uri_safe_identifier + "}"


def _get_new_code_list_scheme_uri(code_list: NewQbCodeList) -> str:
    return _document_relative_uri(f"scheme/{code_list.uri_safe_identifier}")


def _get_default_value_uri_for_code_list_concepts(column: QbColumn, code_list: QbCodeList) -> str:
    column_uri_fragment = _get_column_uri_template_fragment(column)
    if isinstance(code_list, ExistingQbCodeList):
        pass  # TODO: convention-based guess
    elif isinstance(code_list, NewQbCodeList):
        return _document_relative_uri(f"concept/{code_list.uri_safe_identifier}/{column_uri_fragment}")
    else:
        raise Exception(f"Unhandled codelist type {type(code_list)}")
