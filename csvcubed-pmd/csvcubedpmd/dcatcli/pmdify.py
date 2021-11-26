"""
PMDify DCAT Metadata
--------------------

Functionality to convert a CSV-W's DCATv2 metadata into the structure necessary for PMD.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Callable, Tuple
from urllib.parse import urlparse, urljoin

import dateutil.parser
import rdflib
from csvcubedmodels.rdf import ExistingResource
from csvcubedmodels.utils.uri import looks_like_uri
from rdflib import Graph, Literal, URIRef
from rdflib.term import Identifier

from csvcubedpmd.config import pmdconfig
from csvcubedpmd.models.CsvCubedOutputType import CsvCubedOutputType
from csvcubedpmd.models.rdf import pmdcat

_TEMP_PREFIX_URI = URIRef("http://temporary")


def pmdify_dcat(
    csvw_metadata_file_path: Path,
    base_uri: str,
    data_graph_uri: str,
    catalog_metadata_graph_uri: str,
) -> None:
    """
    Modifies `csvw_metadata_file_path` which is a standard csvcubed output to remove the `dcat` dataset metadata.

    Adds a new file located at `csvw_metadata_file_path`.nq containing the catalogue metadata in quad form.
    """
    csvw_metadata_file_path = csvw_metadata_file_path.absolute()
    csvw_rdf_graph = Graph(base=_TEMP_PREFIX_URI)
    with open(csvw_metadata_file_path, "r") as f:
        csvw_file_contents_json = json.load(f)

    rdf_metadata = csvw_file_contents_json["rdfs:seeAlso"]
    rdf_metadata_json = json.dumps(rdf_metadata)

    csvw_rdf_graph.parse(
        data=rdf_metadata_json, publicID=_TEMP_PREFIX_URI, format="json-ld"
    )
    csvw_type = _get_csv_cubed_output_type(csvw_rdf_graph)

    catalog_entry = _get_catalog_entry_from_dcat_dataset(csvw_rdf_graph)
    catalog_record = _generate_pmd_catalog_record(
        catalog_entry, data_graph_uri, catalog_metadata_graph_uri, csvw_type
    )

    _delete_existing_dcat_dataset_metadata(csvw_rdf_graph)

    _replace_uri_substring_in_graph(csvw_rdf_graph, str(_TEMP_PREFIX_URI), base_uri)
    csvw_file_contents_json["rdfs:seeAlso"] = json.loads(
        csvw_rdf_graph.serialize(format="json-ld").decode("UTF-8")  # type: ignore
    )

    initial_id = csvw_file_contents_json.get("@id", "")
    if not looks_like_uri(initial_id):
        initial_id_parsed = urlparse(initial_id)
        csvw_file_contents_json["@id"] = urljoin(base_uri, initial_id_parsed.path)

    # Write removal of dcat metadata from CSV-W to disk.
    with open(csvw_metadata_file_path, "w") as f:
        json.dump(csvw_file_contents_json, f, indent=4)

    # Write separate N-Quads file containing pmdified catalogue metadata.
    catalog_metadata_quads_file_path = Path(f"{csvw_metadata_file_path.absolute()}.nq")
    _write_catalog_metadata_to_quads(
        catalog_record,
        catalog_metadata_quads_file_path,
        catalog_metadata_graph_uri,
        base_uri,
    )


def _replace_uri_substring_in_graph(
    csvw_rdf_graph: Graph, value_to_replace: str, replacement_value: str
) -> None:
    def replace_uri_in_triple(
        triple: Tuple[Identifier, Identifier, Identifier]
    ) -> Tuple[Identifier, Identifier, Identifier]:
        def replace_uri_in_identifier(identifier: Identifier) -> Identifier:
            if isinstance(identifier, URIRef):
                return URIRef(
                    str(identifier).replace(value_to_replace, replacement_value)
                )
            else:
                return identifier

        s, p, o = triple
        return (
            replace_uri_in_identifier(s),
            replace_uri_in_identifier(p),
            replace_uri_in_identifier(o),
        )

    triples = [
        replace_uri_in_triple(t) for t in csvw_rdf_graph.triples((None, None, None))
    ]
    csvw_rdf_graph.remove((None, None, None))
    for triple in triples:
        csvw_rdf_graph.add(triple)


def _generate_pmd_catalog_record(
    catalog_entry: pmdcat.Dataset,
    data_graph_uri: str,
    catalog_metadata_graph_uri: str,
    csv_cubed_output_type: CsvCubedOutputType,
) -> pmdcat.CatalogRecord:
    catalog_entry.dataset_contents = ExistingResource(catalog_entry.uri)

    # N.B. assumes that all URIs are hash URIs, this may not always be the case.
    catalog_entry_uri = re.sub("#.*?$", "#catalog-entry", str(catalog_entry.uri))
    catalog_record_uri = re.sub("#.*?$", "#catalog-record", str(catalog_entry.uri))
    catalog_entry.uri = URIRef(catalog_entry_uri)

    # Catalog -(dcat:record)-> Catalog Record -(foaf:primaryTopic)-> Dataset -(pmdcat:datasetContents)->
    # qb:DataSet/skos:ConceptScheme

    catalog_uri = _get_catalog_uri_to_add_to(csv_cubed_output_type)

    catalog_record = pmdcat.CatalogRecord(catalog_record_uri, catalog_uri)
    catalog_record.title = catalog_entry.title
    catalog_record.label = catalog_entry.label
    catalog_record.description = catalog_entry.description
    catalog_record.comment = catalog_entry.comment
    catalog_record.issued = catalog_record.modified = datetime.now()
    catalog_record.metadata_graph = catalog_metadata_graph_uri
    catalog_record.primary_topic = catalog_entry
    catalog_entry.metadata_graph = catalog_metadata_graph_uri

    catalog_entry.pmdcat_graph = data_graph_uri
    catalog_entry.sparql_endpoint = pmdconfig.SPARQL_ENDPOINT

    return catalog_record


def _get_catalog_uri_to_add_to(csv_cubed_output_type: CsvCubedOutputType) -> str:
    if csv_cubed_output_type == CsvCubedOutputType.SkosConceptScheme:
        return pmdconfig.CODE_LIST_CATALOG_URI
    elif csv_cubed_output_type == CsvCubedOutputType.QbDataSet:
        return pmdconfig.DATASET_CATALOG_URI
    else:
        raise Exception(
            f"Unmatched {CsvCubedOutputType.__name__} '{csv_cubed_output_type}'"
        )


def _write_catalog_metadata_to_quads(
    catalog_record: pmdcat.CatalogRecord,
    catalog_metadata_quads_file_path: Path,
    catalog_metadata_graph_uri: str,
    base_uri: str,
) -> None:
    catalog_metadata_ds = rdflib.Dataset()
    catalog_metadata_graph = catalog_metadata_ds.graph(
        catalog_metadata_graph_uri, base=_TEMP_PREFIX_URI
    )
    assert catalog_metadata_graph is not None

    catalog_metadata_graph = catalog_record.to_graph(catalog_metadata_graph)
    catalog_record.to_graph(catalog_metadata_graph)
    _replace_uri_substring_in_graph(
        catalog_metadata_graph, str(_TEMP_PREFIX_URI), base_uri
    )

    catalog_metadata_ds.serialize(
        str(catalog_metadata_quads_file_path), format="nquads"
    )


def _delete_existing_dcat_dataset_metadata(csvw_graph: Graph) -> None:
    """
    Removes the existing `dcat:Dataset` and associated metadata from the :obj:`csvw_graph` passed in.
    """
    csvw_graph.update(
        """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        DELETE {
            ?dataset a dcat:Dataset;
                a dcat:Resource;
                dcterms:issued ?issued;
                dcterms:modified ?modified;
                rdfs:comment ?comment;
                dcterms:description ?description;
                dcterms:license ?license;
                dcterms:creator ?creator;
                dcterms:publisher ?publisher;
                dcat:landingPage ?landingPage;
                dcat:theme ?theme;
                dcat:keyword ?keyword;
                dcat:contactPoint ?contactPoint;
                dcterms:identifier ?identifier.
        }
        WHERE {
            ?dataset a dcat:Dataset;
                dcterms:issued ?issued;
                dcterms:modified ?modified.

            OPTIONAL { ?dataset rdfs:comment ?comment }.
            OPTIONAL { ?dataset dcterms:description ?description }.
            OPTIONAL { ?dataset dcterms:license ?license }.
            OPTIONAL { ?dataset dcterms:creator ?creator }.
            OPTIONAL { ?dataset dcterms:publisher ?publisher }.
            OPTIONAL { ?dataset dcat:landingPage ?landingPage }.
            OPTIONAL { ?dataset dcat:theme ?theme }.
            OPTIONAL { ?dataset dcat:keyword ?keyword }.
            OPTIONAL { ?dataset dcat:contactPoint ?contactPoint }
            OPTIONAL { ?dataset dcterms:identifier ?identifier }                
        }
        """
    )


def _get_catalog_entry_from_dcat_dataset(csvw_graph: Graph) -> pmdcat.Dataset:
    """
    :return: a :class:`csvcubedpmd.models.rdf.pmdcat.Dataset` to avoid need to convert from dcat to pmdcat object.
    """
    results = list(
        csvw_graph.query(
            """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
        SELECT ?dataset ?title ?label ?issued ?modified ?comment ?description ?license ?creator ?publisher ?landingPage 
            (GROUP_CONCAT(?theme; separator='|') as ?themes) 
            (GROUP_CONCAT(?keyword; separator='|') as ?keywords) 
            ?contactPoint ?identifier
        WHERE {
            ?dataset a dcat:Dataset;
                dcterms:title ?title;
                rdfs:label ?label;
                dcterms:issued ?issued;
                dcterms:modified ?modified.

            OPTIONAL { ?dataset rdfs:comment ?comment }.
            OPTIONAL { ?dataset dcterms:description ?description }.
            OPTIONAL { ?dataset dcterms:license ?license }.
            OPTIONAL { ?dataset dcterms:creator ?creator }.
            OPTIONAL { ?dataset dcterms:publisher ?publisher }.
            OPTIONAL { ?dataset dcat:landingPage ?landingPage }.
            OPTIONAL { ?dataset dcat:theme ?theme }.
            OPTIONAL { ?dataset dcat:keyword ?keyword }.
            OPTIONAL { ?dataset dcat:contactPoint ?contactPoint }
            OPTIONAL { ?dataset dcterms:identifier ?identifier }                
        }
        """
        )
    )

    results = [
        r
        for r in results
        if any([r[k] is not None and r[k] != Literal("") for k in r.labels.keys()])
    ]

    if len(results) != 1:
        raise Exception(f"Expected 1 dcat:Dataset record, found {len(results)}")

    record = results[0]

    pmdcat_dataset = pmdcat.Dataset(record["dataset"])
    pmdcat_dataset.title = str(record["title"])
    pmdcat_dataset.label = str(record["label"])
    pmdcat_dataset.issued = dateutil.parser.isoparse(record["issued"])
    pmdcat_dataset.modified = dateutil.parser.isoparse(record["modified"])
    pmdcat_dataset.comment = _none_or_map(record["comment"], str)
    pmdcat_dataset.description = _none_or_map(record["description"], str)
    pmdcat_dataset.license = _none_or_map(record["license"], str)
    pmdcat_dataset.creator = _none_or_map(record["creator"], str)
    pmdcat_dataset.publisher = _none_or_map(record["publisher"], str)
    pmdcat_dataset.landing_page = _none_or_map(record["landingPage"], str)
    pmdcat_dataset.themes = (
        set() if len(record["themes"]) == 0 else set(str(record["themes"]).split("|"))
    )
    pmdcat_dataset.keywords = (
        set()
        if len(record["keywords"]) == 0
        else set(str(record["keywords"]).split("|"))
    )
    pmdcat_dataset.contact_point = _none_or_map(record["contactPoint"], str)
    pmdcat_dataset.identifier = str(record["identifier"])

    return pmdcat_dataset


def _none_or_map(val: Optional[Any], map_func: Callable[[Any], Any]) -> Optional[Any]:
    if val is None:
        return None
    else:
        return map_func(val)


def _get_csv_cubed_output_type(csvw_rdf_graph: Graph) -> CsvCubedOutputType:
    is_concept_scheme = _ask_query(
        """
        ASK 
        WHERE {
            ?conceptScheme a <http://www.w3.org/2004/02/skos/core#ConceptScheme>.
        }
    """,
        csvw_rdf_graph,
    )

    if is_concept_scheme:
        return CsvCubedOutputType.SkosConceptScheme

    is_qb_dataset = _ask_query(
        """
        ASK 
        WHERE {
            ?qbDataSet a <http://purl.org/linked-data/cube#DataSet>.
        }
    """,
        csvw_rdf_graph,
    )

    if is_qb_dataset:
        return CsvCubedOutputType.QbDataSet

    raise Exception(
        f"Could not determine {CsvCubedOutputType.__name__} for input CSV-W graph."
    )


def _ask_query(query: str, graph: Graph) -> bool:
    results = list(graph.query(query))

    if len(results) == 1:
        result = results[0]
        if isinstance(result, bool):
            return result
        else:
            raise Exception(f"Unexpected ASK query response type {type(result)}")
    else:
        raise Exception(f"Unexpected number of results for ASK query {len(results)}.")
