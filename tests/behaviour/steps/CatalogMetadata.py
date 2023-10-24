from behave import When
from csvcubeddevtools.behaviour.file import get_context_temp_dir_path
from csvcubedmodels.rdf import dcat
from rdflib import Graph

from csvcubed.models.cube.qb.catalog import CatalogMetadata  # from_json_file


@When('loading the existing Catalog Metadata file "{catalog_metadata_file}"')
def step_impl(context, catalog_metadata_file: str):
    catalog_metadata_file_path = (
        get_context_temp_dir_path(context) / catalog_metadata_file
    )
    context.catalog_metadata = CatalogMetadata.from_json_file(
        catalog_metadata_file_path
    )


@When(
    'the Catalog Metadata file is converted to Turtle with dataset URI "{dataset_uri}"'
)
def step_impl(context, dataset_uri: str):
    catalog_metadata: CatalogMetadata = context.catalog_metadata
    dcat_dataset = dcat.Dataset(dataset_uri)
    catalog_metadata.configure_dcat_distribution(dcat_dataset)
    graph = dcat_dataset.to_graph(Graph())
    context.turtle = graph.serialize(format="ttl")
