from datetime import datetime
from pathlib import Path

import rdflib
from csvcubedmodels.rdf import ExistingResource

from csvcubed.cli.buildcsvw.build import build_csvw
from csvcubed.cli.inspectcsvw.metadataprinter import MetadataPrinter

# from csvcubed.writers.helpers.qbwriter.dsdtordfmodelshelper import DsdToRdfModelsHelper
# from csvcubed.writers.helpers.qbwriter.urihelper import UriHelper
from csvcubed.inspect.sparql_handler.csvw_repository import CsvWRepository
from csvcubed.inspect.sparql_handler.data_cube_repository import DataCubeRepository
from csvcubed.inspect.sparql_handler.sparqlquerymanager import (
    select_csvw_catalog_metadata,
    select_data_set_dsd_and_csv_url,
)
from csvcubed.inspect.tableschema import CsvWRdfManager
from csvcubed.models import rdf
from csvcubed.models.cube.qb.catalog import _convert_date_to_date_time
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.rdf import prov
from csvcubed.models.rdf.qbdatasetincatalog import QbDataSetInCatalog
from csvcubed.utils.dict import rdf_resource_to_json_ld
from csvcubed.utils.version import get_csvcubed_version_uri

# cube, errs = build_csvw(
#     Path("out/test_cases/data.csv"), Path("out/test_cases/data.json")
# )

g = rdflib.ConjunctiveGraph()
# g.parse("out/some-title.csv-metadata.json")
# # g.serialize("some-title.ttl", format="turtle")
# # results = select_data_set_dsd_and_csv_url(g)
# results = select_csvw_catalog_metadata(g)
# print()


rdf_mgr = CsvWRdfManager(
    Path(
        "tests/test-cases/cli/inspect/pivoted-multi-measure-dataset/qb-id-10003.csv-metadata.json"
    )
)
dc_repo = DataCubeRepository(rdf_mgr.csvw_repository)
metadata_printer = MetadataPrinter(dc_repo)
# dc_repo.get_cube_identifiers_for_data_set()
# uri_helper = UriHelper(cube)
# dsd_helper = DsdToRdfModelsHelper(cube, uri_helper)
# dsd_helper.generate_data_structure_definitions()
print()


def generate_data_structure_definitions():
    """
    :return: the additional RDF metadata to be serialised in the CSV-W.
    """
    see_also = rdf_resource_to_json_ld(_generate_qb_dataset_dsd_definitions())

    # for dependencies in self._get_rdf_file_dependencies():
    #     see_also += rdf_resource_to_json_ld(dependencies)
    # If the ATTRIBUTE_VALUE_CODELISTS feature flag is set to False, generate attribute value resources to be added to rdfs:seeAlso
    # if not feature_flags.ATTRIBUTE_VALUE_CODELISTS:
    #     for attribute_value in self._get_new_attribute_value_resources():
    #         see_also += rdf_resource_to_json_ld(attribute_value)
    # for unit in self._get_new_unit_resources():
    #     see_also += rdf_resource_to_json_ld(unit)

    return see_also


def _generate_qb_dataset_dsd_definitions(self) -> QbDataSetInCatalog:
    dataset = self._get_qb_dataset_with_catalog_metadata()

    generation_activity = prov.Activity(self._uris.get_build_activity_uri())
    generation_activity.used = ExistingResource(get_csvcubed_version_uri())
    dataset.was_generated_by = generation_activity

    dataset.structure = rdf.qb.DataStructureDefinition(self._uris.get_structure_uri())
    component_ordinal = 1
    for column in self.cube.columns:
        if isinstance(column, QbColumn):
            component_specs_for_col = self._get_qb_component_specs_for_col(
                column.uri_safe_identifier, column.structural_definition
            )
            component_properties_for_col = [
                p for s in component_specs_for_col for p in s.componentProperties
            ]
            dataset.structure.componentProperties |= set(component_properties_for_col)
            for component in component_specs_for_col:
                component.order = component_ordinal
                component_ordinal += 1

            dataset.structure.components |= set(component_specs_for_col)

    if self.cube.is_pivoted_shape:
        dataset.structure.sliceKey.add(self._get_cross_measures_slice_key())

    return dataset


def _get_qb_dataset_with_catalog_metadata(self) -> QbDataSetInCatalog:
    qb_dataset_with_metadata = QbDataSetInCatalog(self._uris.get_dataset_uri())
    self.cube.metadata.configure_dcat_distribution(qb_dataset_with_metadata)
    return qb_dataset_with_metadata


def configure_dcat_distribution(self, distribution) -> None:
    """
    CatalogMetadata properties not currently populated here
    identifier
    creator_uri
    landing_page_uris
    theme_uris
    keywords
    public_contact_point_uri
    uri_safe_identifier_override
    """
    dt_now = datetime.now()
    dt_issued = _convert_date_to_date_time(self.dataset_issued or dt_now)
    distribution.issued = dt_issued
    distribution.modified = _convert_date_to_date_time(
        self.dataset_modified or dt_issued
    )

    distribution.label = distribution.title = self.title
    distribution.description = self.description
    distribution.comment = self.summary
    distribution.publisher = self.publisher_uri
    distribution.license = self.license_uri
    distribution.keywords = set(self.keywords)
    distribution.identifier = self.get_identifier()
    distribution.creator = self.creator_uri
    distribution.landing_page = set(self.landing_page_uris)
    distribution.themes = set(self.theme_uris)
    distribution.keywords = set(self.keywords)


metadata_main = {
    "@context": "http://www.w3.org/ns/csvw",
    "@id": "some-title.csv#dataset",
    "tables": [
        {
            "url": "some-title.csv",
            "tableSchema": {
                "columns": [
                    {
                        "titles": "Dim1",
                        "name": "dim1",
                        "propertyUrl": "some-title.csv#dimension/dimension-1",
                        "valueUrl": "dimension-1.csv#{+dim1}",
                        "required": "true",
                    },
                    {
                        "titles": "Dim2",
                        "name": "dim2",
                        "propertyUrl": "some-title.csv#dimension/dimension-2",
                        "valueUrl": "dimension-2.csv#{+dim2}",
                        "required": "true",
                    },
                    {
                        "titles": "Val",
                        "name": "val",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "some-title.csv#measure/some-measure",
                        "datatype": "int",
                        "required": "false",
                    },
                    {
                        "titles": "Attr1",
                        "name": "attr1",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "some-title.csv#attribute/attribute-1",
                        "valueUrl": "some-title.csv#attribute/attribute-1/{+attr1}",
                        "required": "false",
                    },
                    {
                        "name": "virt_slice",
                        "virtual": "true",
                        "propertyUrl": "rdf:type",
                        "valueUrl": "qb:Slice",
                    },
                    {
                        "name": "virt_slice_structure",
                        "virtual": "true",
                        "propertyUrl": "qb:sliceStructure",
                        "valueUrl": "some-title.csv#slice/cross-measures",
                    },
                    {
                        "name": "virt_obs_val",
                        "virtual": "true",
                        "propertyUrl": "qb:observation",
                        "valueUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                    },
                    {
                        "name": "virt_obs_val_meas",
                        "virtual": "true",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "qb:measureType",
                        "valueUrl": "some-title.csv#measure/some-measure",
                    },
                    {
                        "name": "virt_obs_val_unit",
                        "virtual": "true",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure",
                        "valueUrl": "some-title.csv#unit/some-unit",
                    },
                    {
                        "name": "virt_dim_val_dim1",
                        "virtual": "true",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "some-title.csv#dimension/dimension-1",
                        "valueUrl": "dimension-1.csv#{+dim1}",
                    },
                    {
                        "name": "virt_dim_val_dim2",
                        "virtual": "true",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "some-title.csv#dimension/dimension-2",
                        "valueUrl": "dimension-2.csv#{+dim2}",
                    },
                    {
                        "name": "virt_obs_val_type",
                        "virtual": "true",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "rdf:type",
                        "valueUrl": "qb:Observation",
                    },
                    {
                        "name": "virt_dataSet_val",
                        "virtual": "true",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "qb:dataSet",
                        "valueUrl": "some-title.csv#dataset",
                    },
                ],
                "foreignKeys": [
                    {
                        "columnReference": "dim1",
                        "reference": {
                            "resource": "dimension-1.csv",
                            "columnReference": "uri_identifier",
                        },
                    },
                    {
                        "columnReference": "dim2",
                        "reference": {
                            "resource": "dimension-2.csv",
                            "columnReference": "uri_identifier",
                        },
                    },
                ],
                "primaryKey": ["dim1", "dim2"],
                "aboutUrl": "some-title.csv#slice/{dim1},{dim2}",
            },
        },
        {
            "url": "dimension-1.csv",
            "tableSchema": "dimension-1.table.json",
            "suppressOutput": "true",
        },
        {
            "url": "dimension-2.csv",
            "tableSchema": "dimension-2.table.json",
            "suppressOutput": "true",
        },
    ],
    "rdfs:seeAlso": [
        {
            "@id": "some-title.csv#class/dimension-1",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Class",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
        },
        {
            "@id": "some-title.csv#component/some-measure",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#ComponentSpecification",
                "http://purl.org/linked-data/cube#ComponentSet",
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "some-title.csv#measure/some-measure"}
            ],
            "http://purl.org/linked-data/cube#measure": [
                {"@id": "some-title.csv#measure/some-measure"}
            ],
            "http://purl.org/linked-data/cube#order": [{"@value": 5}],
        },
        {
            "@id": "some-title.csv#component/unit",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#ComponentSpecification",
                "http://purl.org/linked-data/cube#ComponentSet",
            ],
            "http://purl.org/linked-data/cube#attribute": [
                {"@id": "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"}
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"}
            ],
            "http://purl.org/linked-data/cube#componentRequired": [{"@value": "true"}],
            "http://purl.org/linked-data/cube#order": [{"@value": 4}],
        },
        {
            "@id": "some-title.csv#component/dimension-2",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#ComponentSpecification",
                "http://purl.org/linked-data/cube#ComponentSet",
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "some-title.csv#dimension/dimension-2"}
            ],
            "http://purl.org/linked-data/cube#dimension": [
                {"@id": "some-title.csv#dimension/dimension-2"}
            ],
            "http://purl.org/linked-data/cube#order": [{"@value": 2}],
        },
        {
            "@id": "some-title.csv#component/measure-type",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#ComponentSpecification",
                "http://purl.org/linked-data/cube#ComponentSet",
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "http://purl.org/linked-data/cube#measureType"}
            ],
            "http://purl.org/linked-data/cube#dimension": [
                {"@id": "http://purl.org/linked-data/cube#measureType"}
            ],
            "http://purl.org/linked-data/cube#order": [{"@value": 3}],
        },
        {
            "@id": "some-title.csv#dimension/dimension-2",
            "@type": [
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#ComponentProperty",
                "http://purl.org/linked-data/cube#CodedProperty",
                "http://purl.org/linked-data/cube#DimensionProperty",
            ],
            "http://purl.org/linked-data/cube#codeList": [
                {"@id": "dimension-2.csv#code-list"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Dimension 2"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#range": [
                {"@id": "some-title.csv#class/dimension-2"}
            ],
        },
        {
            "@id": "some-title.csv#class/dimension-2",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Class",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
        },
        {
            "@id": "some-title.csv#attribute/attribute-1",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#ComponentProperty",
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property",
                "http://purl.org/linked-data/cube#AttributeProperty",
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Attribute 1"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#subPropertyOf": [
                {"@id": "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus"}
            ],
        },
        {
            "@id": "some-title.csv#component/dimension-1",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#ComponentSpecification",
                "http://purl.org/linked-data/cube#ComponentSet",
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "some-title.csv#dimension/dimension-1"}
            ],
            "http://purl.org/linked-data/cube#dimension": [
                {"@id": "some-title.csv#dimension/dimension-1"}
            ],
            "http://purl.org/linked-data/cube#order": [{"@value": 1}],
        },
        {
            "@id": "some-title.csv#measure/some-measure",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#ComponentProperty",
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property",
                "http://purl.org/linked-data/cube#MeasureProperty",
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Some measure"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#range": [
                {"@id": "http://www.w3.org/2001/XMLSchema#int"}
            ],
        },
        {
            "@id": "some-title.csv#dimension/dimension-1",
            "@type": [
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#ComponentProperty",
                "http://purl.org/linked-data/cube#CodedProperty",
                "http://purl.org/linked-data/cube#DimensionProperty",
            ],
            "http://purl.org/linked-data/cube#codeList": [
                {"@id": "dimension-1.csv#code-list"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Dimension 1"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#range": [
                {"@id": "some-title.csv#class/dimension-1"}
            ],
        },
        {
            "@id": "some-title.csv#dataset",
            "@type": [
                "http://www.w3.org/ns/dcat#Distribution",
                "http://purl.org/linked-data/cube#DataSet",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#Attachable",
                "http://www.w3.org/ns/dcat#Resource",
            ],
            "http://purl.org/dc/terms/creator": [
                {
                    "@id": "https://www.gov.uk/government/organisations/office-for-national-statistics"
                }
            ],
            "http://purl.org/dc/terms/description": [
                {
                    "@type": "https://www.w3.org/ns/iana/media-types/text/markdown#Resource",
                    "@value": "Some description",
                }
            ],
            "http://purl.org/dc/terms/identifier": [{"@value": "Some title"}],
            "http://purl.org/dc/terms/issued": [
                {
                    "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                    "@value": "2022-04-08T00:00:00",
                }
            ],
            "http://purl.org/dc/terms/license": [
                {"@id": "https://creativecommons.org/licenses/by/4.0/"}
            ],
            "http://purl.org/dc/terms/modified": [
                {
                    "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                    "@value": "2022-04-08T00:00:00",
                }
            ],
            "http://purl.org/dc/terms/publisher": [
                {
                    "@id": "https://www.gov.uk/government/organisations/office-for-national-statistics"
                }
            ],
            "http://purl.org/dc/terms/title": [
                {"@language": "en", "@value": "Some title"}
            ],
            "http://purl.org/linked-data/cube#structure": [
                {"@id": "some-title.csv#structure"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#comment": [
                {"@language": "en", "@value": "Some summary"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Some title"}
            ],
            "http://www.w3.org/ns/prov#wasGeneratedBy": [
                {"@id": "some-title.csv#csvcubed-build-activity"}
            ],
        },
        {
            "@id": "some-title.csv#slice/cross-measures",
            "@type": [
                "http://purl.org/linked-data/cube#SliceKey",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#ComponentSet",
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "some-title.csv#dimension/dimension-1"},
                {"@id": "some-title.csv#dimension/dimension-2"},
            ],
        },
        {
            "@id": "some-title.csv#component/attribute-1",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#ComponentSpecification",
                "http://purl.org/linked-data/cube#ComponentSet",
            ],
            "http://purl.org/linked-data/cube#attribute": [
                {"@id": "some-title.csv#attribute/attribute-1"}
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "some-title.csv#attribute/attribute-1"}
            ],
            "http://purl.org/linked-data/cube#componentRequired": [{"@value": "false"}],
            "http://purl.org/linked-data/cube#order": [{"@value": 6}],
        },
        {
            "@id": "some-title.csv#structure",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://purl.org/linked-data/cube#ComponentSet",
                "http://purl.org/linked-data/cube#DataStructureDefinition",
            ],
            "http://purl.org/linked-data/cube#component": [
                {"@id": "some-title.csv#component/dimension-2"},
                {"@id": "some-title.csv#component/measure-type"},
                {"@id": "some-title.csv#component/dimension-1"},
                {"@id": "some-title.csv#component/some-measure"},
                {"@id": "some-title.csv#component/attribute-1"},
                {"@id": "some-title.csv#component/unit"},
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "some-title.csv#dimension/dimension-2"},
                {"@id": "http://purl.org/linked-data/cube#measureType"},
                {"@id": "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"},
                {"@id": "some-title.csv#measure/some-measure"},
                {"@id": "some-title.csv#attribute/attribute-1"},
                {"@id": "some-title.csv#dimension/dimension-1"},
            ],
            "http://purl.org/linked-data/cube#sliceKey": [
                {"@id": "some-title.csv#slice/cross-measures"}
            ],
        },
        {
            "@id": "some-title.csv#dependency/dimension-1",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://rdfs.org/ns/void#Dataset",
            ],
            "http://rdfs.org/ns/void#dataDump": [
                {"@id": "./dimension-1.csv-metadata.json"}
            ],
            "http://rdfs.org/ns/void#uriSpace": [{"@value": "dimension-1.csv#"}],
        },
        {
            "@id": "some-title.csv#dependency/dimension-2",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://rdfs.org/ns/void#Dataset",
            ],
            "http://rdfs.org/ns/void#dataDump": [
                {"@id": "./dimension-2.csv-metadata.json"}
            ],
            "http://rdfs.org/ns/void#uriSpace": [{"@value": "dimension-2.csv#"}],
        },
        {
            "@id": "some-title.csv#attribute/attribute-1/estimated",
            "@type": ["http://www.w3.org/2000/01/rdf-schema#Resource"],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Estimated"}
            ],
        },
        {
            "@id": "some-title.csv#attribute/attribute-1/final",
            "@type": ["http://www.w3.org/2000/01/rdf-schema#Resource"],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Final"}
            ],
        },
        {
            "@id": "some-title.csv#attribute/attribute-1/provisional",
            "@type": ["http://www.w3.org/2000/01/rdf-schema#Resource"],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Provisional"}
            ],
        },
        {
            "@id": "some-title.csv#unit/some-unit",
            "@type": [
                "http://www.ontology-of-units-of-measure.org/resource/om-2/Unit",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://qudt.org/schema/qudt/Unit",
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Some unit"}
            ],
        },
    ],
}

metadata_911 = {
    "@context": "http://www.w3.org/ns/csvw",
    "@id": "some-title.csv#csvqb",
    "tables": [
        {
            "url": "some-title.csv",
            "tableSchema": {
                "columns": [
                    {
                        "titles": "Dim1",
                        "name": "dim1",
                        "propertyUrl": "some-title.csv#dimension/dimension-1",
                        "valueUrl": "dimension-1.csv#{+dim1}",
                        "required": "true",
                    },
                    {
                        "titles": "Dim2",
                        "name": "dim2",
                        "propertyUrl": "some-title.csv#dimension/dimension-2",
                        "valueUrl": "dimension-2.csv#{+dim2}",
                        "required": "true",
                    },
                    {
                        "titles": "Val",
                        "name": "val",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "some-title.csv#measure/some-measure",
                        "datatype": "int",
                        "required": "false",
                    },
                    {
                        "titles": "Attr1",
                        "name": "attr1",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "some-title.csv#attribute/attribute-1",
                        "valueUrl": "some-title.csv#attribute/attribute-1/{+attr1}",
                        "required": "false",
                    },
                    {
                        "name": "virt_slice",
                        "virtual": "true",
                        "propertyUrl": "rdf:type",
                        "valueUrl": "qb:Slice",
                    },
                    {
                        "name": "virt_slice_structure",
                        "virtual": "true",
                        "propertyUrl": "qb:sliceStructure",
                        "valueUrl": "some-title.csv#slice/cross-measures",
                    },
                    {
                        "name": "virt_obs_val",
                        "virtual": "true",
                        "propertyUrl": "qb:observation",
                        "valueUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                    },
                    {
                        "name": "virt_obs_val_meas",
                        "virtual": "true",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "qb:measureType",
                        "valueUrl": "some-title.csv#measure/some-measure",
                    },
                    {
                        "name": "virt_obs_val_unit",
                        "virtual": "true",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure",
                        "valueUrl": "some-title.csv#unit/some-unit",
                    },
                    {
                        "name": "virt_dim_val_dim1",
                        "virtual": "true",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "some-title.csv#dimension/dimension-1",
                        "valueUrl": "dimension-1.csv#{+dim1}",
                    },
                    {
                        "name": "virt_dim_val_dim2",
                        "virtual": "true",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "some-title.csv#dimension/dimension-2",
                        "valueUrl": "dimension-2.csv#{+dim2}",
                    },
                    {
                        "name": "virt_obs_val_type",
                        "virtual": "true",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "rdf:type",
                        "valueUrl": "qb:Observation",
                    },
                    {
                        "name": "virt_dataSet_val",
                        "virtual": "true",
                        "aboutUrl": "some-title.csv#obs/{dim1},{dim2}@some-measure",
                        "propertyUrl": "qb:dataSet",
                        "valueUrl": "some-title.csv#csvqb",
                    },
                ],
                "foreignKeys": [
                    {
                        "columnReference": "dim1",
                        "reference": {
                            "resource": "dimension-1.csv",
                            "columnReference": "uri_identifier",
                        },
                    },
                    {
                        "columnReference": "dim2",
                        "reference": {
                            "resource": "dimension-2.csv",
                            "columnReference": "uri_identifier",
                        },
                    },
                ],
                "primaryKey": ["dim1", "dim2"],
                "aboutUrl": "some-title.csv#slice/{dim1},{dim2}",
            },
        },
        {
            "url": "dimension-1.csv",
            "tableSchema": "dimension-1.table.json",
            "suppressOutput": "true",
        },
        {
            "url": "dimension-2.csv",
            "tableSchema": "dimension-2.table.json",
            "suppressOutput": "true",
        },
    ],
    "rdfs:seeAlso": [
        {
            "@id": "some-title.csv#slice/cross-measures",
            "@type": [
                "http://purl.org/linked-data/cube#SliceKey",
                "http://purl.org/linked-data/cube#ComponentSet",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "some-title.csv#dimension/dimension-1"},
                {"@id": "some-title.csv#dimension/dimension-2"},
            ],
        },
        {
            "@id": "some-title.csv#attribute/attribute-1",
            "@type": [
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property",
                "http://purl.org/linked-data/cube#ComponentProperty",
                "http://purl.org/linked-data/cube#AttributeProperty",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Attribute 1"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#subPropertyOf": [
                {"@id": "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus"}
            ],
        },
        {
            "@id": "some-title.csv#class/dimension-2",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Class",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
        },
        {
            "@id": "some-title.csv#dimension/dimension-2",
            "@type": [
                "http://purl.org/linked-data/cube#ComponentProperty",
                "http://purl.org/linked-data/cube#DimensionProperty",
                "http://purl.org/linked-data/cube#CodedProperty",
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://purl.org/linked-data/cube#codeList": [
                {"@id": "dimension-2.csv#code-list"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Dimension 2"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#range": [
                {"@id": "some-title.csv#class/dimension-2"}
            ],
        },
        {
            "@id": "some-title.csv#component/dimension-2",
            "@type": [
                "http://purl.org/linked-data/cube#ComponentSet",
                "http://purl.org/linked-data/cube#ComponentSpecification",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "some-title.csv#dimension/dimension-2"}
            ],
            "http://purl.org/linked-data/cube#dimension": [
                {"@id": "some-title.csv#dimension/dimension-2"}
            ],
            "http://purl.org/linked-data/cube#order": [{"@value": 2}],
        },
        {
            "@id": "some-title.csv#component/measure-type",
            "@type": [
                "http://purl.org/linked-data/cube#ComponentSet",
                "http://purl.org/linked-data/cube#ComponentSpecification",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "http://purl.org/linked-data/cube#measureType"}
            ],
            "http://purl.org/linked-data/cube#dimension": [
                {"@id": "http://purl.org/linked-data/cube#measureType"}
            ],
            "http://purl.org/linked-data/cube#order": [{"@value": 3}],
        },
        {
            "@id": "some-title.csv#component/unit",
            "@type": [
                "http://purl.org/linked-data/cube#ComponentSet",
                "http://purl.org/linked-data/cube#ComponentSpecification",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://purl.org/linked-data/cube#attribute": [
                {"@id": "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"}
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"}
            ],
            "http://purl.org/linked-data/cube#componentRequired": [{"@value": "true"}],
            "http://purl.org/linked-data/cube#order": [{"@value": 4}],
        },
        {
            "@id": "some-title.csv#component/attribute-1",
            "@type": [
                "http://purl.org/linked-data/cube#ComponentSet",
                "http://purl.org/linked-data/cube#ComponentSpecification",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://purl.org/linked-data/cube#attribute": [
                {"@id": "some-title.csv#attribute/attribute-1"}
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "some-title.csv#attribute/attribute-1"}
            ],
            "http://purl.org/linked-data/cube#componentRequired": [{"@value": "false"}],
            "http://purl.org/linked-data/cube#order": [{"@value": 6}],
        },
        {
            "@id": "some-title.csv#class/dimension-1",
            "@type": [
                "http://www.w3.org/2000/01/rdf-schema#Class",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
        },
        {
            "@id": "some-title.csv#dimension/dimension-1",
            "@type": [
                "http://purl.org/linked-data/cube#ComponentProperty",
                "http://purl.org/linked-data/cube#DimensionProperty",
                "http://purl.org/linked-data/cube#CodedProperty",
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://purl.org/linked-data/cube#codeList": [
                {"@id": "dimension-1.csv#code-list"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Dimension 1"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#range": [
                {"@id": "some-title.csv#class/dimension-1"}
            ],
        },
        {
            "@id": "some-title.csv#csvqb",
            "@type": [
                "http://www.w3.org/ns/dcat#Distribution",
                "http://purl.org/linked-data/cube#Attachable",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
                "http://www.w3.org/ns/dcat#Resource",
                "http://purl.org/linked-data/cube#DataSet",
            ],
            "http://purl.org/dc/terms/created": [
                {
                    "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                    "@value": "2022-04-08T00:00:00",
                }
            ],
            "http://purl.org/dc/terms/creator": [
                {
                    "@id": "https://www.gov.uk/government/organisations/office-for-national-statistics"
                }
            ],
            "http://purl.org/dc/terms/identifier": [{"@value": "Some title"}],
            "http://purl.org/dc/terms/issued": [
                {
                    "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                    "@value": "2022-04-08T00:00:00",
                }
            ],
            "http://purl.org/dc/terms/title": [
                {"@language": "en", "@value": "Some title"}
            ],
            "http://purl.org/linked-data/cube#structure": [
                {"@id": "some-title.csv#structure"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Some title"}
            ],
            "http://www.w3.org/ns/dcat#isDistributionOf": [
                {"@id": "some-title.csv#dataset"}
            ],
            "http://www.w3.org/ns/prov#wasDerivedFrom": [
                {"@id": "https://github.com/GSS-Cogs/csvcubed/releases/tag/v0.1.0.dev0"}
            ],
            "http://www.w3.org/ns/prov#wasGeneratedBy": [
                {"@id": "some-title.csv#csvcubed-build-activity"}
            ],
        },
        {
            "@id": "some-title.csv#measure/some-measure",
            "@type": [
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property",
                "http://purl.org/linked-data/cube#ComponentProperty",
                "http://purl.org/linked-data/cube#MeasureProperty",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Some measure"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#range": [
                {"@id": "http://www.w3.org/2001/XMLSchema#int"}
            ],
        },
        {
            "@id": "some-title.csv#component/some-measure",
            "@type": [
                "http://purl.org/linked-data/cube#ComponentSet",
                "http://purl.org/linked-data/cube#ComponentSpecification",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "some-title.csv#measure/some-measure"}
            ],
            "http://purl.org/linked-data/cube#measure": [
                {"@id": "some-title.csv#measure/some-measure"}
            ],
            "http://purl.org/linked-data/cube#order": [{"@value": 5}],
        },
        {
            "@id": "some-title.csv#component/dimension-1",
            "@type": [
                "http://purl.org/linked-data/cube#ComponentSet",
                "http://purl.org/linked-data/cube#ComponentSpecification",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "some-title.csv#dimension/dimension-1"}
            ],
            "http://purl.org/linked-data/cube#dimension": [
                {"@id": "some-title.csv#dimension/dimension-1"}
            ],
            "http://purl.org/linked-data/cube#order": [{"@value": 1}],
        },
        {
            "@id": "some-title.csv#structure",
            "@type": [
                "http://purl.org/linked-data/cube#ComponentSet",
                "http://purl.org/linked-data/cube#DataStructureDefinition",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://purl.org/linked-data/cube#component": [
                {"@id": "some-title.csv#component/attribute-1"},
                {"@id": "some-title.csv#component/measure-type"},
                {"@id": "some-title.csv#component/dimension-2"},
                {"@id": "some-title.csv#component/unit"},
                {"@id": "some-title.csv#component/some-measure"},
                {"@id": "some-title.csv#component/dimension-1"},
            ],
            "http://purl.org/linked-data/cube#componentProperty": [
                {"@id": "some-title.csv#dimension/dimension-2"},
                {"@id": "some-title.csv#measure/some-measure"},
                {"@id": "http://purl.org/linked-data/cube#measureType"},
                {"@id": "some-title.csv#dimension/dimension-1"},
                {"@id": "some-title.csv#attribute/attribute-1"},
                {"@id": "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"},
            ],
            "http://purl.org/linked-data/cube#sliceKey": [
                {"@id": "some-title.csv#slice/cross-measures"}
            ],
        },
        {
            "@id": "some-title.csv#dataset",
            "@type": [
                "http://www.w3.org/ns/dcat#Dataset",
                "http://www.w3.org/ns/dcat#Resource",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://purl.org/dc/terms/creator": [
                {
                    "@id": "https://www.gov.uk/government/organisations/office-for-national-statistics"
                }
            ],
            "http://purl.org/dc/terms/description": [
                {
                    "@type": "https://www.w3.org/ns/iana/media-types/text/markdown#Resource",
                    "@value": "Some description",
                }
            ],
            "http://purl.org/dc/terms/identifier": [{"@value": "Some title"}],
            "http://purl.org/dc/terms/issued": [
                {
                    "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                    "@value": "2022-04-08T00:00:00",
                }
            ],
            "http://purl.org/dc/terms/license": [
                {"@id": "https://creativecommons.org/licenses/by/4.0/"}
            ],
            "http://purl.org/dc/terms/modified": [
                {
                    "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                    "@value": "2022-04-08T00:00:00",
                }
            ],
            "http://purl.org/dc/terms/publisher": [
                {
                    "@id": "https://www.gov.uk/government/organisations/office-for-national-statistics"
                }
            ],
            "http://purl.org/dc/terms/title": [
                {"@language": "en", "@value": "Some title"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#comment": [
                {"@language": "en", "@value": "Some summary"}
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Some title"}
            ],
            "http://www.w3.org/ns/dcat#distribution": [{"@id": "some-title.csv#csvqb"}],
        },
        {
            "@id": "some-title.csv#dependency/dimension-1",
            "@type": [
                "http://rdfs.org/ns/void#Dataset",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://rdfs.org/ns/void#dataDump": [
                {"@id": "./dimension-1.csv-metadata.json"}
            ],
            "http://rdfs.org/ns/void#uriSpace": [{"@value": "dimension-1.csv#"}],
        },
        {
            "@id": "some-title.csv#dependency/dimension-2",
            "@type": [
                "http://rdfs.org/ns/void#Dataset",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://rdfs.org/ns/void#dataDump": [
                {"@id": "./dimension-2.csv-metadata.json"}
            ],
            "http://rdfs.org/ns/void#uriSpace": [{"@value": "dimension-2.csv#"}],
        },
        {
            "@id": "some-title.csv#attribute/attribute-1/estimated",
            "@type": ["http://www.w3.org/2000/01/rdf-schema#Resource"],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Estimated"}
            ],
        },
        {
            "@id": "some-title.csv#attribute/attribute-1/final",
            "@type": ["http://www.w3.org/2000/01/rdf-schema#Resource"],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Final"}
            ],
        },
        {
            "@id": "some-title.csv#attribute/attribute-1/provisional",
            "@type": ["http://www.w3.org/2000/01/rdf-schema#Resource"],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Provisional"}
            ],
        },
        {
            "@id": "some-title.csv#unit/some-unit",
            "@type": [
                "http://qudt.org/schema/qudt/Unit",
                "http://www.ontology-of-units-of-measure.org/resource/om-2/Unit",
                "http://www.w3.org/2000/01/rdf-schema#Resource",
            ],
            "http://www.w3.org/2000/01/rdf-schema#label": [
                {"@language": "en", "@value": "Some unit"}
            ],
        },
    ],
}
