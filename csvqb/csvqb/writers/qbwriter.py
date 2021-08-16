"""
CSV-qb Writer
-------------

Output writer for CSV-qb
"""
import itertools
import json
import re
from pathlib import Path
from typing import Tuple, Dict, Any, List, Iterable
import rdflib
from sharedmodels import rdf
from sharedmodels.rdf import qb, skos
from sharedmodels.rdf.resource import (
    Resource,
    ExistingResource,
    maybe_existing_resource,
)

from csvqb.models.cube import *
from csvqb.utils.uri import get_last_uri_part, csvw_column_name_safe, looks_like_uri
from csvqb.utils.qb.cube import get_columns_of_dsd_type
from csvqb.utils.dict import rdf_resource_to_json_ld
from .skoscodelistwriter import SkosCodeListWriter, CODE_LIST_NOTATION_COLUMN_NAME
from .writerbase import WriterBase
from ..models.cube.csvqb.components.arbitraryrdf import (
    RdfSerialisationHint,
)
from ..models.rdf.qbdatasetincatalog import QbDataSetInCatalog


VIRT_UNIT_COLUMN_NAME = "virt_unit"


class QbWriter(WriterBase):
    def __init__(self, cube: QbCube):
        self.cube: QbCube = cube
        self.csv_file_name: str = f"{cube.metadata.uri_safe_identifier}.csv"

    def write(self, output_folder: Path):
        tables = [
            {
                "url": self.csv_file_name,
                "tableSchema": {
                    "columns": self._generate_csvw_columns_for_cube(),
                    "foreignKeys": self._generate_foreign_keys_for_cube(),
                    "primaryKey": self._get_primary_key_columns(),
                    "aboutUrl": self._get_about_url(),
                },
            }
        ]

        tables += self._get_table_references_needed_for_foreign_keys()

        self._output_new_code_list_csvws(output_folder)

        # todo: Local units haven't been defined anywhere yet!
        # todo: Unit multiplier functionality hasn't been output.

        csvw_metadata = {
            "@context": "http://www.w3.org/ns/csvw",
            "@id": self._doc_rel_uri("dataset"),
            "tables": tables,
            "rdfs:seeAlso": rdf_resource_to_json_ld(
                self._generate_qb_dataset_dsd_definitions()
            ),
        }

        with open(output_folder / f"{self.csv_file_name}-metadata.json", "w+") as f:
            json.dump(csvw_metadata, f, indent=4)

        if self.cube.data is not None:
            self.cube.data.to_csv(output_folder / self.csv_file_name, index=False)

    def _doc_rel_uri(self, uri_fragment: str) -> str:
        """
        URIs declared in the `columns` section of the CSV-W are relative to the CSV's location.
        URIs declared in the JSON-LD metadata section of the CSV-W are relative to the metadata file's location.

        This function makes both point to the same base location - the CSV file's location. This ensures that we
        can talk about the same resources in the `columns` section and the JSON-LD metadata section.
        """
        return f"{self.csv_file_name}#{uri_fragment}"

    def _output_new_code_list_csvws(self, output_folder: Path) -> None:
        for column in get_columns_of_dsd_type(self.cube, NewQbDimension):
            if isinstance(column.component.code_list, NewQbCodeList):
                code_list_writer = SkosCodeListWriter(column.component.code_list)
                code_list_writer.write(output_folder)

    def _generate_csvw_columns_for_cube(self) -> List[Dict[str, Any]]:
        columns = [self._generate_csvqb_column(c) for c in self.cube.columns]
        virtual_columns = self._generate_virtual_columns_for_cube()
        return columns + virtual_columns

    def _get_columns_for_foreign_keys(self) -> List[QbColumn[NewQbDimension]]:
        columns = []
        for col in get_columns_of_dsd_type(self.cube, NewQbDimension):
            if col.component.code_list is not None and isinstance(
                col.component.code_list, NewQbCodeList
            ):
                columns.append(col)

        return columns

    def _get_table_references_needed_for_foreign_keys(self) -> List[dict]:
        tables = []
        for col in self._get_columns_for_foreign_keys():
            code_list = col.component.code_list
            assert isinstance(code_list, NewQbCodeList)

            tables.append(
                {
                    "url": f"{code_list.metadata.uri_safe_identifier}.csv",
                    "tableSchema": f"{code_list.metadata.uri_safe_identifier}.table.json",
                    "suppressOutput": True,
                }
            )

        return tables

    def _generate_foreign_keys_for_cube(self) -> List[dict]:
        foreign_keys: List[dict] = []
        for col in self._get_columns_for_foreign_keys():
            code_list = col.component.code_list
            assert isinstance(code_list, NewQbCodeList)

            foreign_keys.append(
                {
                    "columnReference": csvw_column_name_safe(col.uri_safe_identifier),
                    "reference": {
                        "resource": f"{code_list.metadata.uri_safe_identifier}.csv",
                        "columnReference": CODE_LIST_NOTATION_COLUMN_NAME,
                    },
                }
            )

        return foreign_keys

    def _generate_virtual_columns_for_cube(self) -> List[Dict[str, Any]]:
        virtual_columns = []
        for column in self.cube.columns:
            if isinstance(column, QbColumn):
                if isinstance(column.component, QbObservationValue):
                    virtual_columns += self._generate_virtual_columns_for_obs_val(
                        column.component
                    )

        return virtual_columns

    def _generate_virtual_columns_for_obs_val(
        self, obs_val: QbObservationValue
    ) -> List[Dict[str, Any]]:
        virtual_columns: List[dict] = []
        unit = obs_val.unit
        if unit is not None:
            virtual_columns.append(
                {
                    "name": VIRT_UNIT_COLUMN_NAME,
                    "virtual": True,
                    "propertyUrl": "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure",
                    "valueUrl": self._get_unit_uri(unit),
                }
            )
            # todo: We can't do the same thing with unti multipler unfortunately. Perhaps we should attach the unit
            #  measure to the qb:DataSet as per the normalised standard and then de-normalise it when we upload to PMD?
        if isinstance(obs_val, QbSingleMeasureObservationValue):
            virtual_columns.append(
                {
                    "name": "virt_measure",
                    "virtual": True,
                    "propertyUrl": "http://purl.org/linked-data/cube#measureType",
                    "valueUrl": self._get_measure_uri(obs_val.measure),
                }
            )
        return virtual_columns

    def _get_qb_dataset_with_catalog_metadata(self) -> QbDataSetInCatalog:
        qb_dataset_with_metadata = QbDataSetInCatalog(self._doc_rel_uri("dataset"))
        self.cube.metadata.configure_dcat_dataset(qb_dataset_with_metadata)
        return qb_dataset_with_metadata

    def _generate_qb_dataset_dsd_definitions(self) -> QbDataSetInCatalog:
        dataset = self._get_qb_dataset_with_catalog_metadata()
        dataset.structure = rdf.qb.DataStructureDefinition(
            self._doc_rel_uri("structure")
        )
        for column in self.cube.columns:
            if isinstance(column, QbColumn):
                component_specs_for_col = self._get_qb_component_specs_for_col(
                    column.uri_safe_identifier, column.component
                )
                component_properties_for_col = [
                    p for s in component_specs_for_col for p in s.componentProperties
                ]
                dataset.structure.componentProperties |= set(
                    component_properties_for_col
                )
                dataset.structure.components |= set(component_specs_for_col)

        return dataset

    def _get_qb_component_specs_for_col(
        self, column_name_uri_safe: str, component: QbDataStructureDefinition
    ) -> Iterable[rdf.qb.ComponentSpecification]:
        if isinstance(component, QbDimension):
            return [
                self._get_qb_dimension_specification(column_name_uri_safe, component)
            ]
        elif isinstance(component, QbAttribute):
            return [
                self._get_qb_attribute_specification(column_name_uri_safe, component)
            ]
        elif isinstance(component, QbMultiUnits):
            return [self._get_qb_units_column_specification(column_name_uri_safe)]
        elif isinstance(component, QbMultiMeasureDimension):
            return self._get_qb_measure_dimension_specifications(component)
        elif isinstance(component, QbObservationValue):
            return self._get_qb_obs_val_specifications(component)
        else:
            raise Exception(f"Unhandled component type {type(component)}")

    def _get_obs_val_data_type(self) -> str:
        observation_value_columns = get_columns_of_dsd_type(
            self.cube, QbObservationValue
        )
        # Given the data shapes we accept as input, there should always be one (and only one) Observation Value
        # column in a cube.
        observation_value_column = observation_value_columns[0]
        data_type = observation_value_column.component.data_type
        if looks_like_uri(data_type):
            # is already a full URI
            return data_type
        else:
            # Is not a URI so it should be xsd:`data_type`.
            return str(rdflib.XSD[data_type])

    def _get_qb_units_column_specification(
        self, column_name_uri_safe: str
    ) -> rdf.qb.AttributeComponentSpecification:
        component = rdf.qb.AttributeComponentSpecification(
            self._doc_rel_uri(f"component/{column_name_uri_safe}")
        )
        component.componentRequired = True
        component.attribute = ExistingResource(
            "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
        )
        component.componentProperties.add(component.attribute)

        return component

    def _get_qb_obs_val_specifications(
        self, observation_value: QbObservationValue
    ) -> List[rdf.qb.ComponentSpecification]:
        specs: List[rdf.qb.ComponentSpecification] = []
        unit = observation_value.unit
        if unit is not None:
            unit_uri_safe_identifier = self._get_unit_uri_safe_identifier(unit)
            specs.append(
                self._get_qb_units_column_specification(unit_uri_safe_identifier)
            )

        if isinstance(observation_value, QbSingleMeasureObservationValue):
            specs.append(
                self._get_qb_measure_component_specification(observation_value.measure)
            )
        elif isinstance(observation_value, QbMultiMeasureObservationValue):
            pass
        else:
            raise Exception(
                f"Unmatched Observation value component of type {type(observation_value)}."
            )

        return specs

    @staticmethod
    def _get_unit_uri_safe_identifier(unit: QbUnit) -> str:
        if isinstance(unit, ExistingQbUnit):
            return get_last_uri_part(unit.unit_uri)
        elif isinstance(unit, NewQbUnit):
            return unit.uri_safe_identifier
        else:
            raise Exception(f"Unhandled unit type {type(unit)}")

    def _get_qb_measure_dimension_specifications(
        self, measure_dimension: QbMultiMeasureDimension
    ) -> List[rdf.qb.MeasureComponentSpecification]:
        measure_specs: List[rdf.qb.MeasureComponentSpecification] = []
        for measure in measure_dimension.measures:
            measure_specs.append(self._get_qb_measure_component_specification(measure))

        return measure_specs

    def _get_qb_measure_component_specification(
        self, measure: QbMeasure
    ) -> rdf.qb.MeasureComponentSpecification:
        if isinstance(measure, ExistingQbMeasure):
            component_uri = self._doc_rel_uri(
                f"component/{get_last_uri_part(measure.measure_uri)}"
            )
            component = rdf.qb.MeasureComponentSpecification(component_uri)
            component.measure = ExistingResource(measure.measure_uri)
            component.componentProperties.add(component.measure)

            measure.copy_arbitrary_triple_fragments_to_resources(
                {RdfSerialisationHint.Component: component}
            )

            return component
        elif isinstance(measure, NewQbMeasure):
            component = rdf.qb.MeasureComponentSpecification(
                self._doc_rel_uri(f"component/{measure.uri_safe_identifier}")
            )
            component.measure = rdf.qb.MeasureProperty(
                self._doc_rel_uri(f"measure/{measure.uri_safe_identifier}")
            )
            component.measure.label = measure.label
            component.measure.comment = measure.description
            component.measure.subPropertyOf = maybe_existing_resource(
                measure.parent_measure_uri
            )
            component.measure.source = maybe_existing_resource(measure.source_uri)
            component.measure.range = ExistingResource(self._get_obs_val_data_type())
            component.componentProperties.add(component.measure)

            measure.copy_arbitrary_triple_fragments_to_resources(
                {
                    RdfSerialisationHint.Component: component,
                    RdfSerialisationHint.Property: component.measure,
                }
            )

            return component
        else:
            raise Exception(f"Unhandled measure type {type(measure)}")

    def _get_qb_dimension_specification(
        self, column_name_uri_safe: str, dimension: QbDimension
    ) -> rdf.qb.DimensionComponentSpecification:
        if isinstance(dimension, ExistingQbDimension):
            component = rdf.qb.DimensionComponentSpecification(
                self._doc_rel_uri(f"component/{column_name_uri_safe}")
            )
            component.dimension = ExistingResource(dimension.dimension_uri)
            dimension.copy_arbitrary_triple_fragments_to_resources(
                {RdfSerialisationHint.Component: component}
            )
        elif isinstance(dimension, NewQbDimension):
            component = rdf.qb.DimensionComponentSpecification(
                self._doc_rel_uri(f"component/{dimension.uri_safe_identifier}")
            )
            component.dimension = rdf.qb.DimensionProperty(
                self._doc_rel_uri(f"dimension/{dimension.uri_safe_identifier}")
            )
            component.dimension.label = dimension.label
            component.dimension.comment = dimension.description
            component.dimension.subPropertyOf = maybe_existing_resource(
                dimension.parent_dimension_uri
            )
            component.dimension.source = maybe_existing_resource(dimension.source_uri)
            component.dimension.range = ExistingResource(rdflib.SKOS.Concept)

            dimension.copy_arbitrary_triple_fragments_to_resources(
                {
                    RdfSerialisationHint.Component: component,
                    RdfSerialisationHint.Property: component.dimension,
                }
            )

            if dimension.code_list is not None:
                component.dimension.code_list = self._get_code_list_resource(
                    dimension.code_list
                )

        else:
            raise Exception(f"Unhandled dimension component type {type(dimension)}.")

        component.componentProperties.add(component.dimension)

        return component

    def _get_code_list_resource(
        self, code_list: QbCodeList
    ) -> Resource[skos.ConceptScheme]:
        if isinstance(code_list, ExistingQbCodeList):
            return ExistingResource(code_list.concept_scheme_uri)
        elif isinstance(code_list, NewQbCodeList):
            # The resource is created elsewhere. There is a separate CSV-W definition for the code-list
            return ExistingResource(self._get_new_code_list_scheme_uri(code_list))
        else:
            raise Exception(f"Unhandled code list type {type(code_list)}")

    def _get_qb_attribute_specification(
        self, column_name_uri_safe: str, attribute: QbAttribute
    ) -> rdf.qb.AttributeComponentSpecification:
        if isinstance(attribute, ExistingQbAttribute):
            component = rdf.qb.AttributeComponentSpecification(
                self._doc_rel_uri(f"component/{column_name_uri_safe}")
            )
            component.attribute = ExistingResource(attribute.attribute_uri)

            attribute.copy_arbitrary_triple_fragments_to_resources(
                {RdfSerialisationHint.Component: component}
            )
        elif isinstance(attribute, NewQbAttribute):
            component = rdf.qb.AttributeComponentSpecification(
                self._doc_rel_uri(f"component/{attribute.uri_safe_identifier}")
            )
            component.attribute = rdf.qb.AttributeProperty(
                self._doc_rel_uri(f"attribute/{attribute.uri_safe_identifier}")
            )
            component.attribute.label = attribute.label
            component.attribute.comment = attribute.description
            component.attribute.subPropertyOf = maybe_existing_resource(
                attribute.parent_attribute_uri
            )
            component.attribute.source = maybe_existing_resource(attribute.source_uri)
            # todo: Find some way to link the codelist we have to the
            #  ComponentProperty?

            attribute.copy_arbitrary_triple_fragments_to_resources(
                {
                    RdfSerialisationHint.Component: component,
                    RdfSerialisationHint.Property: component.attribute,
                }
            )
        else:
            raise Exception(f"Unhandled attribute component type {type(attribute)}.")

        component.componentRequired = attribute.is_required
        component.componentProperties.add(component.attribute)

        return component

    def _generate_csvqb_column(self, column: CsvColumn) -> Dict[str, Any]:
        csvw_col: Dict[str, Any] = {
            "titles": column.csv_column_title,
            "name": csvw_column_name_safe(column.uri_safe_identifier),
        }

        if isinstance(column, SuppressedCsvColumn):
            csvw_col["suppressOutput"] = True
        elif isinstance(column, QbColumn):
            self._define_csvw_column_for_qb_column(csvw_col, column)
        else:
            raise Exception(
                f"Unhandled column type ({type(column)}) with title '{column.csv_column_title}'"
            )

        return csvw_col

    def _define_csvw_column_for_qb_column(
        self, csvw_col: dict, column: QbColumn
    ) -> None:
        (
            property_url,
            default_value_url,
        ) = self._get_default_property_value_uris_for_column(column)
        if property_url is not None:
            csvw_col["propertyUrl"] = property_url

        if column.output_uri_template is not None:
            # User-specified value overrides our default guess.
            csvw_col["valueUrl"] = column.output_uri_template
        elif default_value_url is not None:
            csvw_col["valueUrl"] = default_value_url

        if isinstance(column.component, QbObservationValue):
            csvw_col["datatype"] = column.component.data_type

        csvw_col["required"] = (
            isinstance(column.component, QbDimension)
            or isinstance(column.component, QbObservationValue)
            or isinstance(column.component, QbMultiUnits)
            or isinstance(column.component, QbMultiMeasureDimension)
            or (
                isinstance(column.component, QbAttribute)
                and column.component.is_required
            )
        )

    def _get_default_property_value_uris_for_multi_units(
        self, column: QbColumn, multi_units: QbMultiUnits
    ) -> Tuple[str, str]:
        column_template_fragment = self._get_column_uri_template_fragment(column)
        all_units_new = all([isinstance(u, NewQbUnit) for u in multi_units.units])
        all_units_existing = all(
            [isinstance(u, ExistingQbUnit) for u in multi_units.units]
        )

        unit_value_uri: str
        if all_units_new:
            unit_value_uri = self._doc_rel_uri(f"unit/{column_template_fragment}")
        elif all_units_existing:
            unit_value_uri = column_template_fragment
        else:
            # todo: Come up with a solution for this!
            raise Exception(
                "Cannot handle a mix of new units and existing defined units."
            )

        return (
            "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure",
            unit_value_uri,
        )

    def _get_default_property_value_uris_for_multi_measure(
        self, column: QbColumn, measure_dimension: QbMultiMeasureDimension
    ) -> Tuple[str, str]:
        column_template_fragment = self._get_column_uri_template_fragment(column)
        all_measures_new = all(
            [isinstance(m, NewQbMeasure) for m in measure_dimension.measures]
        )
        all_measures_existing = all(
            [isinstance(m, ExistingQbMeasure) for m in measure_dimension.measures]
        )

        measure_value_uri: str
        if all_measures_new:
            measure_value_uri = self._doc_rel_uri(f"measure/{column_template_fragment}")
        elif all_measures_existing:
            measure_value_uri = column_template_fragment
        else:
            # todo: Come up with a solution for this!
            raise Exception(
                "Cannot handle a mix of new measures and existing defined measures."
            )

        return "http://purl.org/linked-data/cube#measureType", measure_value_uri

    def _get_default_property_value_uris_for_column(
        self, column: QbColumn
    ) -> Tuple[Optional[str], Optional[str]]:
        if isinstance(column.component, QbDimension):
            return self._get_default_property_value_uris_for_dimension(column)
        elif isinstance(column.component, QbAttribute):
            return self._get_default_property_value_uris_for_attribute(column)
        elif isinstance(column.component, QbMultiUnits):
            return self._get_default_property_value_uris_for_multi_units(
                column, column.component
            )
        elif isinstance(column.component, QbMultiMeasureDimension):
            return self._get_default_property_value_uris_for_multi_measure(
                column, column.component
            )
        elif isinstance(column.component, QbObservationValue):
            return None, None
        else:
            raise Exception(f"Unhandled component type {type(column.component)}")

    def _get_default_property_value_uris_for_dimension(
        self, column: QbColumn[QbDimension]
    ) -> Tuple[str, Optional[str]]:
        dimension = column.component
        if isinstance(dimension, ExistingQbDimension):
            return dimension.dimension_uri, self._get_column_uri_template_fragment(
                column
            )
        elif isinstance(dimension, NewQbDimension):
            local_dimension_uri = self._doc_rel_uri(
                f"dimension/{dimension.uri_safe_identifier}"
            )
            value_uri = self._get_column_uri_template_fragment(column)
            if dimension.code_list is not None:
                value_uri = self._get_default_value_uri_for_code_list_concepts(
                    column, dimension.code_list
                )

            return local_dimension_uri, value_uri
        else:
            raise Exception(f"Unhandled dimension type {type(dimension)}")

    def _get_default_property_value_uris_for_attribute(
        self, column: QbColumn[QbAttribute]
    ) -> Tuple[str, str]:
        attribute = column.component
        column_uri_fragment = self._get_column_uri_template_fragment(column)
        value_uri = self._get_column_uri_template_fragment(column)
        if isinstance(attribute, ExistingQbAttribute):
            if len(attribute.new_attribute_values) > 0:
                # NewQbAttributeValues defined here.
                value_uri = self._doc_rel_uri(
                    f"attribute/{column.uri_safe_identifier}/{column_uri_fragment}"
                )
            # Else: Existing attribute values defined elsewhere. The user *should* have defined an output_uri_template.
            # N.B. We can't do mix-and-match New/Existing attribute values.

            return attribute.attribute_uri, value_uri
        elif isinstance(attribute, NewQbAttribute):
            local_attribute_uri = self._doc_rel_uri(
                f"attribute/{attribute.uri_safe_identifier}"
            )

            if len(attribute.new_attribute_values) > 0:
                # NewQbAttributeValues defined here.
                value_uri = self._doc_rel_uri(
                    f"attribute/{attribute.uri_safe_identifier}/{column_uri_fragment}"
                )
            # Else: Existing attribute values defined elsewhere. The user *should* have defined an
            # output_uri_template.
            # N.B. We can't do mix-and-match New/Existing attribute values.

            return local_attribute_uri, value_uri
        else:
            raise Exception(f"Unhandled attribute type {type(attribute)}")

    def _get_column_uri_template_fragment(
        self, column: CsvColumn, escape_value: bool = False
    ) -> str:
        if escape_value:
            return "{" + csvw_column_name_safe(column.uri_safe_identifier) + "}"

        return "{+" + csvw_column_name_safe(column.uri_safe_identifier) + "}"

    def _get_new_code_list_scheme_uri(self, code_list: NewQbCodeList) -> str:
        return f"{code_list.metadata.uri_safe_identifier}.csv#scheme/{code_list.metadata.uri_safe_identifier}"

    _external_code_list_pattern = re.compile("^(.*)/concept-scheme/(.*)$")
    _dataset_local_code_list_pattern = re.compile("^(.*)#scheme/(.*)$")

    def _get_default_value_uri_for_code_list_concepts(
        self, column: CsvColumn, code_list: QbCodeList
    ) -> str:
        column_uri_fragment = self._get_column_uri_template_fragment(column)
        if isinstance(code_list, ExistingQbCodeList):
            external_match = self._external_code_list_pattern.match(
                code_list.concept_scheme_uri
            )
            local_match = self._dataset_local_code_list_pattern.match(
                code_list.concept_scheme_uri
            )
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
            return self._doc_rel_uri(
                f"concept/{code_list.metadata.uri_safe_identifier}/{column_uri_fragment}"
            )
        else:
            raise Exception(f"Unhandled codelist type {type(code_list)}")

    def _get_unit_uri(self, unit: QbUnit) -> str:
        if isinstance(unit, ExistingQbUnit):
            return unit.unit_uri
        elif isinstance(unit, NewQbUnit):
            return self._doc_rel_uri(f"unit/{unit.uri_safe_identifier}")
        else:
            raise Exception(f"Unmatched unit type {type(unit)}")

    def _get_measure_uri(self, measure: QbMeasure) -> str:
        if isinstance(measure, ExistingQbMeasure):
            return measure.measure_uri
        elif isinstance(measure, NewQbMeasure):
            return self._doc_rel_uri(f"measure/{measure.uri_safe_identifier}")
        else:
            raise Exception(f"Unmatched measure type {type(measure)}")

    def _get_about_url(self) -> str:
        # Todo: Dimensions are currently appended in the order in which the appear in the cube.
        #       We may want to alter this in the future so that the ordering is from
        #       least entropic dimension -> most entropic.
        #       E.g. http://base-uri/observations/male/1996/all-males-1996
        about_url = self._doc_rel_uri("obs")
        multi_measure_col = ""
        for c in self.cube.columns:
            if isinstance(c, QbColumn):
                if isinstance(c.component, QbDimension):
                    about_url = (
                        about_url
                        + f"/{{+{csvw_column_name_safe(c.uri_safe_identifier)}}}"
                    )
                elif isinstance(c.component, QbMultiMeasureDimension):
                    multi_measure_col = csvw_column_name_safe(c.uri_safe_identifier)
        if len(multi_measure_col) != 0:
            about_url = about_url + f"/{{+{multi_measure_col}}}"
        return about_url

    def _get_primary_key_columns(self) -> List[str]:
        dimension_columns: Iterable[QbColumn] = itertools.chain(
            get_columns_of_dsd_type(self.cube, QbDimension),
            get_columns_of_dsd_type(self.cube, QbMultiMeasureDimension),
        )

        return [csvw_column_name_safe(c.csv_column_title) for c in dimension_columns]
