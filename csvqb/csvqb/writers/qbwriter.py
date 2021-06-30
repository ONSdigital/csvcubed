"""Output writer for CSV-qb"""
import json
import re
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import rdflib
from csvqb.models.cube import *
from sharedmodels.rdf import qb
from sharedmodels.rdf.rdfresource import ExistingResource, maybe_existing


def write_metadata(cube: Cube, output_file: Path) -> None:
    tables = [
        {
            "url": "output.csv",  # todo
            "tableSchema": {
                "columns": [_generate_csvqb_column(c) for c in cube.columns]
            }
        }
    ]

    dataset_definition = _generate_cube_rdf_definition(cube)

    # todo: Need to decide on the catalogue metadata's structure and add it to `rdfs:seeAlso` below.

    csvw_metadata = {
        "@context": "http://www.w3.org/ns/csvw",
        "@id": _document_relative_uri("dataset"),
        "tables": tables,
        "rdfs:label": cube.metadata.title,
        "dc:title": cube.metadata.title,
        "rdfs:comment": cube.metadata.summary,
        "dc:description": cube.metadata.description,
        "rdfs:seeAlso": dataset_definition
    }

    with open(output_file, "w+") as f:
        json.dump(csvw_metadata, f, indent=4)


def _generate_cube_rdf_definition(cube: Cube) -> dict:
    dataset = qb.DataSet(_document_relative_uri("dataset"))
    dataset.structure = qb.DataStructureDefinition(_document_relative_uri("structure"))
    for column in cube.columns:
        if isinstance(column, QbColumn):
            component_spec = _get_qb_component_specification(column.uri_safe_identifier, column.component)
            # todo: Figure out which one to add to, both?
            # dataset.structure.componentProperties.add()
            dataset.structure.components.add(component_spec)

    # Serialise to json-ld then de-serialise it to add to the dictionary we are building.
    g = rdflib.Graph()
    dataset.to_graph(g)
    return json.loads(g.serialize(format="json-ld") or "{}")


def _get_qb_component_specification(column_name_uri_safe: str,
                                    component: QbDataStructureDefinition) -> qb.ComponentSpecification:
    # todo: complete me!
    if isinstance(component, QbDimension):
        pass
    elif isinstance(component, QbAttribute):
        return _get_qb_attribute_specification(column_name_uri_safe, component)
    elif isinstance(component, QbMultiUnits):
        pass
    elif isinstance(component, QbMultiMeasureDimension):
        pass
    elif isinstance(component, QbObservationValue):
        pass
    else:
        raise Exception(f"Unhandled component type {type(component)}")

    raise Exception("Not implemented yet")


def _get_qb_attribute_specification(column_name_uri_safe: str,
                                    attribute: QbAttribute) -> qb.AttributeComponentSpecification:
    if isinstance(attribute, ExistingQbAttribute):
        attribute_component_uri = _document_relative_uri(f"component/{column_name_uri_safe}")
        attribute_component = qb.AttributeComponentSpecification(attribute_component_uri)
        attribute_component.attribute = ExistingResource(attribute.attribute_uri)
    elif isinstance(attribute, NewQbAttribute):
        attribute_component = qb.AttributeComponentSpecification(
            _document_relative_uri(f"component/{attribute.uri_safe_identifier}"))
        attribute_component.attribute = qb.AttributeProperty(
            _document_relative_uri(f"attribute/{attribute.uri_safe_identifier}"))
        attribute_component.attribute.label = attribute.label
        attribute_component.attribute.comment = attribute.description
        attribute_component.attribute.subPropertyOf = maybe_existing(attribute.parent_attribute_uri)
        # todo: Find some way to link the codelist we have to the ComponentProperty?
        # todo: Implement sourceUri on all of our ComponentProperties.
    else:
        raise Exception(f"Unhandled attribute component type {type(attribute)}.")

    attribute_component.componentRequired = attribute.is_required
    attribute_component.componentProperties.add(attribute_component.attribute)
    return attribute_component


def _document_relative_uri(uri_fragment: str) -> str:
    return f"#{uri_fragment}"


def _generate_csvqb_column(column: CsvColumn) -> Dict[str, Any]:
    csvw_col: Dict[str, Any] = {
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
        Tuple[Optional[str], Optional[str]]:
    if isinstance(column.component, QbDimension):
        return _get_default_property_value_uris_for_dimension(column)
    elif isinstance(column.component, QbAttribute):
        return _get_default_property_value_uris_for_attribute(column)
    elif isinstance(column.component, QbMultiUnits):
        # todo: How do we deal with the situation where the user wants to specify a mixture of local
        #  and remote units in the same column?
        local_unit_value_uri = _document_relative_uri(f"unit/{_get_column_uri_template_fragment(column)}")
        return "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure", local_unit_value_uri
    elif isinstance(column.component, QbMultiMeasureDimension):
        # todo: How do we deal with the situation where the user wants to specify a mixture of local
        #  and remote measures in the same column?
        local_measure_value_uri = _document_relative_uri(
            f"measure/{_get_column_uri_template_fragment(column)}")
        return "http://purl.org/linked-data/cube#measureType", local_measure_value_uri
    elif isinstance(column.component, QbObservationValue):
        return None, None
    else:
        raise Exception(f"Unhandled component type {type(column.component)}")


def _get_default_property_value_uris_for_dimension(column: QbColumn[QbDimension]) -> Tuple[str, Optional[str]]:
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


def _get_default_property_value_uris_for_attribute(column: QbColumn[QbAttribute]) -> Tuple[str, str]:
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


external_code_list_pattern = re.compile("^(.*)/concept-scheme/(.*)$")
dataset_local_code_list_pattern = re.compile("^(.*)#scheme/(.*)$")


def _get_default_value_uri_for_code_list_concepts(column: QbColumn, code_list: QbCodeList) -> str:
    column_uri_fragment = _get_column_uri_template_fragment(column)
    if isinstance(code_list, ExistingQbCodeList):
        external_match = external_code_list_pattern.match(code_list.concept_scheme_uri)
        local_match = dataset_local_code_list_pattern.match(code_list.concept_scheme_uri)
        if external_match:
            m: re.Match = external_match
            # ConceptScheme URI:
            # http://gss-data.org.uk/def/concept-scheme/{code-list-name}
            # Concept URI:
            # http://gss-data.org.uk/def/concept-scheme/{code-list-name}/{notation}
            return f"{m.group(1)}/concept-scheme/{m.group(2)}/{column_uri_fragment}"
        elif local_match:
            m: re.Match = local_match
            # ConceptScheme URI:
            # http://gss-data.org.uk/data/gss_data/{family-name}/{dataset-root-name}#scheme/{code-list-name}
            # Concept URI:
            # http://gss-data.org.uk/data/gss_data/{family-name}/{dataset-root-name}#concept/{code-list-name}/{notation}
            return f"{m.group(1)}#concept/{m.group(2)}/{column_uri_fragment}"
        else:
            # Unexpected code-list URI. Does not match expected conventions.
            return column_uri_fragment

    elif isinstance(code_list, NewQbCodeList):
        return _document_relative_uri(f"concept/{code_list.uri_safe_identifier}/{column_uri_fragment}")
    else:
        raise Exception(f"Unhandled codelist type {type(code_list)}")
