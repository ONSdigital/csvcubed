"""
QB DSD Helper
-------------

Help Generate the DSD necessary for an RDF Data Cube.
"""
import logging
from dataclasses import dataclass
from typing import Iterable, List, Set

from csvcubedmodels import rdf
from csvcubedmodels.rdf import (
    ExistingResource,
    ExistingResourceWithLiteral,
    Resource,
    maybe_existing_resource,
    rdfs,
    skos,
)
from csvcubedmodels.rdf.dependency import RdfGraphDependency

from csvcubed.models.cube.cube import QbCube
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.cube.qb.components.arbitraryrdf import RdfSerialisationHint
from csvcubed.models.cube.qb.components.attribute import (
    ExistingQbAttribute,
    NewQbAttribute,
    NewQbAttributeValue,
    QbAttribute,
    QbAttributeLiteral,
)
from csvcubed.models.cube.qb.components.codelist import (
    ExistingQbCodeList,
    NewQbCodeList,
    NewQbCodeListInCsvW,
    QbCodeList,
)
from csvcubed.models.cube.qb.components.datastructuredefinition import (
    QbStructuralDefinition,
)
from csvcubed.models.cube.qb.components.dimension import (
    ExistingQbDimension,
    NewQbDimension,
    QbDimension,
)
from csvcubed.models.cube.qb.components.measure import (
    ExistingQbMeasure,
    NewQbMeasure,
    QbMeasure,
)
from csvcubed.models.cube.qb.components.measuresdimension import QbMultiMeasureDimension
from csvcubed.models.cube.qb.components.observedvalue import QbObservationValue
from csvcubed.models.cube.qb.components.unit import NewQbUnit, QbUnit
from csvcubed.models.cube.qb.components.unitscolumn import QbMultiUnits
from csvcubed.models.rdf import prov
from csvcubed.models.rdf.newattributevalueresource import NewAttributeValueResource
from csvcubed.models.rdf.newunitresource import NewUnitResource
from csvcubed.models.rdf.qbdatasetincatalog import QbDataSetInCatalog
from csvcubed.utils.dict import rdf_resource_to_json_ld
from csvcubed.utils.uri import get_data_type_uri_from_str, get_last_uri_part
from csvcubed.utils.version import get_csvcubed_version_uri
from csvcubed.writers.helpers.skoscodelistwriter.newresourceurigenerator import (
    NewResourceUriGenerator as SkosCodeListNewResourceUriGenerator,
)
from csvcubed.writers.skoscodelistwriter import SkosCodeListWriter

from .urihelper import UriHelper

_logger = logging.getLogger(__name__)


@dataclass
class DsdToRdfModelsHelper:
    cube: QbCube
    _uris: UriHelper

    def generate_data_structure_definitions(self) -> List[dict]:
        """
        :return: the additional RDF metadata to be serialised in the CSV-W.
        """
        see_also = rdf_resource_to_json_ld(self._generate_qb_dataset_dsd_definitions())

        for dependencies in self._get_rdf_file_dependencies():
            see_also += rdf_resource_to_json_ld(dependencies)

        for attribute_value in self._get_new_attribute_value_resources():
            see_also += rdf_resource_to_json_ld(attribute_value)

        for unit in self._get_new_unit_resources():
            see_also += rdf_resource_to_json_ld(unit)

        return see_also

    def _get_rdf_file_dependencies(self) -> List[RdfGraphDependency]:
        """
        Define RDF dependencies of this CSV-W file which help the end-user understand the triples expressed by this CSV-W.

        :return: RDF resource models to define dependencies on other RDF files.
        """
        rdf_file_dependencies: List[RdfGraphDependency] = []

        dimension_columns = self.cube.get_columns_of_dsd_type(NewQbDimension)
        for column in dimension_columns:
            dimension = column.structural_definition
            code_list = dimension.code_list
            if isinstance(code_list, NewQbCodeList):
                dependency = RdfGraphDependency(
                    self._uris.get_void_dataset_dependency_uri(
                        code_list.metadata.uri_safe_identifier
                    )
                )

                code_list_writer = SkosCodeListWriter(code_list, self.cube.uri_style)
                dependency.uri_space = (
                    code_list_writer.uri_helper.get_uri_prefix_for_doc()
                )

                dependency.dependent_rdf_file_location = ExistingResource(
                    f"./{code_list_writer.csv_metadata_file_name}"
                )

                rdf_file_dependencies.append(dependency)

        return rdf_file_dependencies

    def _get_new_attribute_value_resources(self) -> List[NewAttributeValueResource]:
        """
        :return: RDF resource models to define New Attribute Values
        """
        new_attribute_value_resources: List[NewAttributeValueResource] = []
        attribute_columns = self.cube.get_columns_of_dsd_type(QbAttribute)
        for column in attribute_columns:
            if isinstance(column.structural_definition, NewQbAttribute):
                column_identifier = column.structural_definition.uri_safe_identifier
            else:
                column_identifier = column.uri_safe_identifier

            for value in column.structural_definition.new_attribute_values:  # type: ignore
                assert isinstance(value, NewQbAttributeValue)

                attribute_value_uri = self._uris.get_new_attribute_value_uri(
                    column_identifier, value.uri_safe_identifier
                )
                new_attribute_value_resource = NewAttributeValueResource(
                    attribute_value_uri
                )
                new_attribute_value_resource.label = value.label
                new_attribute_value_resource.comment = value.description
                new_attribute_value_resource.source_uri = maybe_existing_resource(
                    value.source_uri
                )
                new_attribute_value_resource.parent_attribute_value_uri = (
                    maybe_existing_resource(value.parent_attribute_value_uri)
                )

                _logger.debug(
                    "Generated New Attribute Value %s.",
                    new_attribute_value_resource.uri,
                )

                new_attribute_value_resources.append(new_attribute_value_resource)

        return new_attribute_value_resources

    def _get_new_unit_resources(self) -> List[NewUnitResource]:
        """
        :return: RDF Resources to defined new units
        """
        units: Set[QbUnit] = {
            u
            for col in self.cube.get_columns_of_dsd_type(QbMultiUnits)
            for u in col.structural_definition.units  # type: ignore
        }

        units |= {
            col.structural_definition.unit
            for col in self.cube.get_columns_of_dsd_type(QbObservationValue)
            if col.structural_definition.unit is not None
        }

        def get_new_base_units(u: QbUnit) -> set[QbUnit]:
            if (
                isinstance(u, NewQbUnit)
                and u.base_unit is not None
                and isinstance(u.base_unit, NewQbUnit)
            ):
                new_base_units = get_new_base_units(u.base_unit)
                new_base_units.add(u.base_unit)

                return new_base_units

            return set()

        units |= {base_unit for u in units for base_unit in get_new_base_units(u)}

        new_units: Set[NewQbUnit] = {u for u in units if isinstance(u, NewQbUnit)}

        new_unit_resources: List[NewUnitResource] = []
        for unit in new_units:
            unit_uri = self._uris.get_unit_uri(unit)
            new_unit_resource = NewUnitResource(unit_uri)
            new_unit_resource.label = unit.label
            new_unit_resource.comment = unit.description
            new_unit_resource.source_uri = maybe_existing_resource(unit.source_uri)

            maybe_base_unit_uri = (
                None
                if unit.base_unit is None
                else self._uris.get_unit_uri(unit.base_unit)
            )

            new_unit_resource.base_unit_uri = maybe_existing_resource(
                maybe_base_unit_uri
            )
            new_unit_resource.base_unit_scaling_factor = unit.base_unit_scaling_factor

            new_unit_resource.has_qudt_quantity_kind = maybe_existing_resource(
                unit.qudt_quantity_kind_uri
            )
            new_unit_resource.qudt_conversion_multiplier = (
                unit.si_base_unit_conversion_multiplier
            )

            _logger.debug("Generated new unit resource %s.", new_unit_resource.uri)

            new_unit_resources.append(new_unit_resource)

        return new_unit_resources

    def _generate_qb_dataset_dsd_definitions(self) -> QbDataSetInCatalog:
        dataset = self._get_qb_dataset_with_catalog_metadata()

        generation_activity = prov.Activity(self._uris.get_build_activity_uri())
        generation_activity.used = ExistingResource(get_csvcubed_version_uri())
        dataset.was_generated_by = generation_activity

        dataset.structure = rdf.qb.DataStructureDefinition(
            self._uris.get_structure_uri()
        )
        component_ordinal = 1
        for column in self.cube.columns:
            if isinstance(column, QbColumn):
                component_specs_for_col = self._get_qb_component_specs_for_col(
                    column.uri_safe_identifier, column.structural_definition
                )
                component_properties_for_col = [
                    p for s in component_specs_for_col for p in s.componentProperties
                ]
                dataset.structure.componentProperties |= set(
                    component_properties_for_col
                )
                for component in component_specs_for_col:
                    component.order = component_ordinal
                    component_ordinal += 1

                dataset.structure.components |= set(component_specs_for_col)

        if self.cube.is_pivoted_shape:
            dataset.structure.sliceKey.add(self._get_cross_measures_slice_key())

        return dataset

    def _get_qb_dataset_with_catalog_metadata(self) -> QbDataSetInCatalog:
        qb_dataset_with_metadata = QbDataSetInCatalog(self._uris.get_dataset_uri())
        self.cube.metadata.configure_dcat_dataset(qb_dataset_with_metadata)
        return qb_dataset_with_metadata

    def _get_cross_measures_slice_key(self) -> rdf.qb.SliceKey:
        # Setting up Slice Key for slices which range over measures.
        _logger.debug("Setting the slice key across measures")

        slice_key = rdf.qb.SliceKey(self._uris.get_slice_key_across_measures_uri())
        _logger.debug("Slice key uri across measures is '%s'", slice_key.uri)

        for dimension_column in self.cube.get_columns_of_dsd_type(QbDimension):
            _logger.debug(
                "Adding the component property for dimension column with title '%s' into the slice key",
                dimension_column.csv_column_title,
            )
            dimension_uri: str = self._uris.get_dimension_uri(
                dimension_column.structural_definition
            )

            slice_key.componentProperties.add(ExistingResource(dimension_uri))

        _logger.debug(
            "Added %d component properties to the slice key.",
            len(slice_key.componentProperties),
        )
        return slice_key

    def _get_qb_component_specs_for_col(
        self, column_name_uri_safe: str, component: QbStructuralDefinition
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
            raise TypeError(f"Unhandled component type {type(component)}")

    def _get_qb_units_column_specification(
        self, column_name_uri_safe: str
    ) -> rdf.qb.AttributeComponentSpecification:
        component = rdf.qb.AttributeComponentSpecification(
            self._uris.get_component_uri(column_name_uri_safe)
        )
        component.componentRequired = True
        component.attribute = ExistingResource(
            "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
        )
        component.componentProperties.add(component.attribute)

        _logger.debug(
            "Generated units component %s.",
            component.uri,
        )

        return component

    def _get_qb_obs_val_specifications(
        self, observation_value: QbObservationValue
    ) -> List[rdf.qb.ComponentSpecification]:
        specs: List[rdf.qb.ComponentSpecification] = [
            # We always output the measure-dimension style of the QB spec.
            # so each observation need to have a dimension specifying the measure type.
            self._get_measure_type_dimension_component_spec()
        ]

        unit = observation_value.unit
        if unit is not None:
            specs.append(self._get_qb_units_column_specification("unit"))

        if observation_value.is_pivoted_shape_observation:
            assert observation_value.measure is not None
            specs.append(
                self._get_qb_measure_component_specification(observation_value.measure)
            )

        return specs

    def _get_measure_type_dimension_component_spec(
        self,
    ) -> rdf.qb.DimensionComponentSpecification:
        measure_dimension_spec = rdf.qb.DimensionComponentSpecification(
            self._uris.get_component_uri("measure-type")
        )
        measure_dimension_spec.dimension = ExistingResource(
            "http://purl.org/linked-data/cube#measureType"
        )
        measure_dimension_spec.componentProperties.add(measure_dimension_spec.dimension)
        return measure_dimension_spec

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
        measure_uri = self._uris.get_measure_uri(measure)
        if isinstance(measure, ExistingQbMeasure):
            component_uri = self._uris.get_component_uri(get_last_uri_part(measure_uri))
            component = rdf.qb.MeasureComponentSpecification(component_uri)
            component.measure = ExistingResource(measure_uri)
            component.componentProperties.add(component.measure)

            measure.copy_arbitrary_triple_fragments_to_resources(
                {RdfSerialisationHint.Component: component}
            )
        elif isinstance(measure, NewQbMeasure):
            component = rdf.qb.MeasureComponentSpecification(
                self._uris.get_component_uri(measure.uri_safe_identifier)
            )
            component.measure = rdf.qb.MeasureProperty(measure_uri)
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

        else:
            raise TypeError(f"Unhandled measure type {type(measure)}")

        _logger.debug(
            "Generated component %s with measure %s.",
            component.uri,
            component.measure.uri,
        )

        return component

    def _get_qb_dimension_specification(
        self, column_name_uri_safe: str, dimension: QbDimension
    ) -> rdf.qb.DimensionComponentSpecification:
        dimension_uri = self._uris.get_dimension_uri(dimension)

        if isinstance(dimension, ExistingQbDimension):
            component = rdf.qb.DimensionComponentSpecification(
                self._uris.get_component_uri(column_name_uri_safe)
            )
            component.dimension = ExistingResource(dimension_uri)
            dimension.copy_arbitrary_triple_fragments_to_resources(
                {RdfSerialisationHint.Component: component}
            )
        elif isinstance(dimension, NewQbDimension):
            component = rdf.qb.DimensionComponentSpecification(
                self._uris.get_component_uri(dimension.uri_safe_identifier)
            )
            component.dimension = rdf.qb.DimensionProperty(dimension_uri)
            component.dimension.label = dimension.label
            component.dimension.comment = dimension.description
            component.dimension.subPropertyOf = maybe_existing_resource(
                dimension.parent_dimension_uri
            )
            component.dimension.source = maybe_existing_resource(dimension.source_uri)
            component.dimension.range = rdfs.Class(
                self._uris.get_class_uri(dimension.uri_safe_identifier)
            )

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
            raise TypeError(f"Unhandled dimension component type {type(dimension)}.")

        component.componentProperties.add(component.dimension)

        _logger.debug(
            "Generated component %s with dimension %s.",
            component.uri,
            component.dimension.uri,
        )

        return component

    def _get_qb_attribute_specification(
        self, column_name_uri_safe: str, attribute: QbAttribute
    ) -> rdf.qb.AttributeComponentSpecification:
        attribute_uri = self._uris.get_attribute_uri(attribute)

        if isinstance(attribute, ExistingQbAttribute):
            component = rdf.qb.AttributeComponentSpecification(
                self._uris.get_component_uri(column_name_uri_safe)
            )
            if isinstance(attribute, QbAttributeLiteral):
                component.attribute = ExistingResourceWithLiteral(attribute_uri)
                component.attribute.range = ExistingResource(
                    get_data_type_uri_from_str(attribute.data_type)
                )
            else:
                component.attribute = ExistingResource(attribute_uri)

            attribute.copy_arbitrary_triple_fragments_to_resources(
                {RdfSerialisationHint.Component: component}
            )
        elif isinstance(attribute, NewQbAttribute):
            component = rdf.qb.AttributeComponentSpecification(
                self._uris.get_component_uri(attribute.uri_safe_identifier)
            )
            component.attribute = rdf.qb.AttributeProperty(attribute_uri)
            component.attribute.label = attribute.label
            component.attribute.comment = attribute.description
            component.attribute.subPropertyOf = maybe_existing_resource(
                attribute.parent_attribute_uri
            )
            component.attribute.source = maybe_existing_resource(attribute.source_uri)
            # TODO: Find some way to link the codelist we have to the ComponentProperty?
            if isinstance(attribute, QbAttributeLiteral):
                component.attribute.range = ExistingResource(
                    get_data_type_uri_from_str(attribute.data_type)
                )
            attribute.copy_arbitrary_triple_fragments_to_resources(
                {
                    RdfSerialisationHint.Component: component,
                    RdfSerialisationHint.Property: component.attribute,
                }
            )
        else:
            raise TypeError(f"Unhandled attribute component type {type(attribute)}.")

        component.componentRequired = attribute.is_required
        component.componentProperties.add(component.attribute)

        _logger.debug(
            "Generated component %s with attribute %s.",
            component.uri,
            component.attribute.uri,
        )

        return component

    def _get_code_list_resource(
        self, code_list: QbCodeList
    ) -> Resource[skos.ConceptScheme]:
        if isinstance(code_list, ExistingQbCodeList):
            return ExistingResource(code_list.concept_scheme_uri)
        elif isinstance(code_list, NewQbCodeList):
            # The resource is created elsewhere. There is a separate CSV-W definition for the code-list
            return ExistingResource(
                SkosCodeListNewResourceUriGenerator(
                    code_list, self.cube.uri_style
                ).get_scheme_uri()
            )
        elif isinstance(code_list, NewQbCodeListInCsvW):
            return ExistingResource(code_list.concept_scheme_uri)
        else:
            raise TypeError(f"Unhandled codelist type {type(code_list)}")

    def _get_obs_val_data_type(self) -> str:
        observation_value_columns = self.cube.get_columns_of_dsd_type(
            QbObservationValue
        )
        # Given the data shapes we accept as input, there should always be one (and only one) Observation Value
        # column in a cube.
        observation_value_column = observation_value_columns[0]
        data_type = observation_value_column.structural_definition.data_type
        return get_data_type_uri_from_str(data_type)
