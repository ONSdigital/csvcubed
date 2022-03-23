"""
PMDify DCAT Metadata
--------------------

Functionality to convert a CSV-W's DCATv2 metadata into the structure necessary for PMD.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Callable, Tuple, List
from urllib.parse import urlparse, urljoin

import dateutil.parser
import rdflib
from csvcubedmodels.rdf import ExistingResource
from csvcubedmodels.utils.uri import looks_like_uri
from rdflib import Graph, Literal, URIRef
from rdflib.query import ResultRow
from rdflib.term import Identifier

from csvcubedpmd.config import pmdconfig
from csvcubedpmd.models.CsvCubedOutputType import CsvCubedOutputType
from csvcubedpmd.models.rdf import pmdcat
from csvcubedpmd.utils import rdflibutils
from csvcubedpmd.utils.sparql import ask

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
        csvw_file_contents: str = f.read()

    csvw_file_contents_json: dict = json.loads(csvw_file_contents)

    csvw_rdf_graph.parse(data=csvw_file_contents, publicID=_TEMP_PREFIX_URI, format="json-ld")
    _remove_csvw_rdf_from_graph(csvw_rdf_graph)

    csvw_type = _get_csv_cubed_output_type(csvw_rdf_graph)

    catalog_entry = _get_catalog_entry_from_dcat_dataset(csvw_rdf_graph)
    catalog_record = _generate_pmd_catalog_record(
        catalog_entry, data_graph_uri, catalog_metadata_graph_uri, csvw_type
    )

    _delete_existing_dcat_metadata(csvw_rdf_graph)

    _replace_uri_substring_in_graph(csvw_rdf_graph, str(_TEMP_PREFIX_URI), base_uri)

    # Remove RDF which is not of CSV-W origin from the JSON, we'll add the relevant info back later.
    _remove_non_csvw_rdf_from_json_ld(csvw_file_contents_json)

    csvw_file_contents_json["rdfs:seeAlso"] = rdflibutils.serialise_to_json_ld(
        csvw_rdf_graph
    )

    initial_id = csvw_file_contents_json.get("@id", "")
    if not looks_like_uri(initial_id):
        initial_id_parsed = urlparse(initial_id)
        csvw_file_contents_json["@id"] = urljoin(base_uri, initial_id_parsed.path)

    # Write removal of dcat metadata from CSV-W to disk.
    with open(csvw_metadata_file_path, "w") as f:
        json.dump(csvw_file_contents_json, f, indent=4)

    # # Write separate N-Quads file containing pmdified catalogue metadata.
    catalog_metadata_quads_file_path = Path(f"{csvw_metadata_file_path.absolute()}.nq")
    _write_catalog_metadata_to_quads(
        catalog_record,
        catalog_metadata_quads_file_path,
        catalog_metadata_graph_uri,
        base_uri,
        csvw_type
    )


def _remove_csvw_rdf_from_graph(csvw_rdf_graph):
    columns_list_items = list(csvw_rdf_graph.query("""
        PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX csvw: <http://www.w3.org/ns/csvw#>
        
        SELECT ?listItem 
        WHERE {
            {
                [] csvw:column/rdfs:rest*/rdfs:first* ?listItem.
            } UNION {
                [] csvw:columnReference/rdfs:rest*/rdfs:first* ?listItem.
            }
        }    
    """))

    for list_item_identifier in [item[0] for item in columns_list_items]:
        csvw_rdf_graph.remove((list_item_identifier, None, None))
        csvw_rdf_graph.remove((None, None, list_item_identifier))

    for (sub, pred, obj) in list(csvw_rdf_graph.triples((None, None, None))):
        if str(pred).startswith("http://www.w3.org/ns/csvw#"):
            csvw_rdf_graph.remove((sub, pred, obj))


def _remove_non_csvw_rdf_from_json_ld(csvw_file_contents_json: dict) -> None:
    rdf_keys = [k for k in csvw_file_contents_json.keys() if ":" in k or looks_like_uri(k)]
    for key in rdf_keys:
        del csvw_file_contents_json[key]


def _set_pmdcat_type_on_dataset_contents(
    csvw_rdf_graph: Graph, csvw_type: CsvCubedOutputType
) -> None:
    if csvw_type == CsvCubedOutputType.QbDataSet:
        csvw_rdf_graph.update(
            """           
            PREFIX qb:      <http://purl.org/linked-data/cube#>
            PREFIX pmdcat:  <http://publishmydata.com/pmdcat#>

            INSERT { ?dataset a pmdcat:DataCube. } WHERE { [] pmdcat:datasetContents ?dataset. }
            """
        )
    elif csvw_type == CsvCubedOutputType.SkosConceptScheme:
        csvw_rdf_graph.update(
            """
            PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
            PREFIX pmdcat:  <http://publishmydata.com/pmdcat#>

            INSERT { ?conceptScheme a pmdcat:ConceptScheme. } WHERE { [] pmdcat:datasetContents ?conceptScheme. }
            """
        )
    else:
        raise Exception(f"Unmatched CSV-W type '{csvw_type}'")


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
        replace_uri_in_triple((s, p, o))
        for (s, p, o) in csvw_rdf_graph.triples((None, None, None))
        if isinstance(s, Identifier) and isinstance(p, Identifier) and isinstance(o, Identifier)
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

    # N.B. assumes that all URIs are hash URIs, this may not always be the case.
    catalog_entry_uri = f"{catalog_entry.uri}-catalog-entry"
    catalog_record_uri = f"{catalog_entry.uri}-catalog-record"
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
    csvw_type: CsvCubedOutputType
) -> None:
    catalog_metadata_ds = rdflib.Dataset()
    catalog_metadata_graph = catalog_metadata_ds.graph(
        catalog_metadata_graph_uri, base=_TEMP_PREFIX_URI
    )
    assert catalog_metadata_graph is not None

    catalog_metadata_graph = catalog_record.to_graph(catalog_metadata_graph)
    _set_pmdcat_type_on_dataset_contents(catalog_metadata_graph, csvw_type)

    _replace_uri_substring_in_graph(
        catalog_metadata_graph, str(_TEMP_PREFIX_URI), base_uri
    )

    catalog_metadata_ds.serialize(
        str(catalog_metadata_quads_file_path), format="nquads"
    )


def _delete_existing_dcat_metadata(csvw_graph: Graph) -> None:
    _delete_existing_dcat_dataset_metadata(csvw_graph)
    _delete_legacy_existing_dcat_catalog_record(csvw_graph)


def _delete_legacy_existing_dcat_catalog_record(csvw_graph: Graph) -> None:
    # Now to delete any catalogue entries already present. This can occur in legacy code-lists.
    csvw_graph.update("""
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        DELETE {
            ?catalogRecord a dcat:CatalogRecord;
                ?p ?o.
                
            <http://gss-data.org.uk/catalog/vocabularies> dcat:record ?catalogRecord.
        }
        WHERE {
            ?catalogRecord a dcat:CatalogRecord.
            
            OPTIONAL { 
                <http://gss-data.org.uk/catalog/vocabularies> dcat:record ?catalogRecord.
            }
            
            OPTIONAL {
                ?catalogRecord ?p ?o. 
            }
        }
    """)


def _delete_existing_dcat_dataset_metadata(csvw_graph: Graph) -> None:
    """
    Removes the existing `dcat:Dataset` and associated metadata from the :obj:`csvw_graph` passed in.
    """
    csvw_graph.update(
        """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX pmdcat: <http://publishmydata.com/pmdcat#>

        DELETE {
            ?dataset a dcat:Dataset, pmdcat:Dataset;
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
                dcterms:identifier ?identifier;
                pmdcat:graph ?graph;
                pmdcat:datasetContents ?datasetContents;
                ?p ?o.
                
            ?datasetContents a pmdcat:DatasetContents, pmdcat:DataCube, pmdcat:ConceptScheme.
            
            ?s ?p ?dataset.               
        }
        WHERE {
            {
                SELECT DISTINCT ?dataset
                WHERE {
                    {
                        ?dataset a dcat:Dataset.        
                    } UNION {
                        ?dataset a pmdcat:Dataset.
                    }
                }
            }
            
            ?dataset dcterms:issued ?issued;
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
            OPTIONAL { ?dataset pmdcat:graph ?graph }
            OPTIONAL { 
                ?dataset pmdcat:datasetContents ?datasetContents.
                OPTIONAL {
                    ?datasetContents a pmdcat:DatasetContents, pmdcat:DataCube, pmdcat:ConceptScheme.
                } 
            }          
            OPTIONAL {
                # Make sure to delete all related triples if the ?dataset is only an instance of 
                # dcat:Dataset of pmdcat:Dataset (and nothing else).
                
                FILTER NOT EXISTS {
                    ?dataset a ?type.
                    FILTER(?type NOT IN (dcat:Dataset, pmdcat:Dataset)).
                }
                
                {
                    ?dataset ?p ?o.
                } UNION {     
                    ?s ?p ?dataset.
                }
            }
        }
        """
    )


def _get_catalog_entry_from_dcat_dataset(csvw_graph: Graph) -> pmdcat.Dataset:
    """
    :return: a :class:`csvcubedpmd.models.rdf.pmdcat.Dataset` to avoid need to convert from dcat to pmdcat object.
    """

    catalog_metadata_query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX pmdcat:  <http://publishmydata.com/pmdcat#>
    
        SELECT ?dataset ?title ?label ?issued ?modified ?comment ?description ?license ?creator ?publisher 
            (GROUP_CONCAT(?landingPage ; separator='|') as ?landingPages) 
            (GROUP_CONCAT(?theme; separator='|') as ?themes) 
            (GROUP_CONCAT(?keyword; separator='|') as ?keywords) 
            ?contactPoint ?identifier ?datasetContents
        WHERE {
            {
                SELECT DISTINCT ?dataset
                WHERE {
                    {
                        ?dataset a dcat:Dataset.        
                    } UNION {
                        ?dataset a pmdcat:Dataset.
                    }
                }
            }
        
            ?dataset dcterms:title ?title;
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
            OPTIONAL { ?dataset dcat:contactPoint ?contactPoint }.
            OPTIONAL { ?dataset dcterms:identifier ?identifier }.   
            OPTIONAL { ?dataset pmdcat:datasetContents ?datasetContents }.           
        }
        """

    results = [
        r
        for r in list(csvw_graph.query(catalog_metadata_query))
        if isinstance(r, ResultRow) and isinstance(r.labels, dict) and
           any([r[k] is not None and r[k] != Literal("") for k in r.labels.keys()])
    ]

    if len(results) != 1:
        raise Exception(f"Expected 1 dcat:Dataset record, found {len(results)}")

    record = results[0].asdict()

    pmdcat_dataset = pmdcat.Dataset(str(record["dataset"]))
    pmdcat_dataset.title = str(record["title"])
    pmdcat_dataset.label = str(record["label"])
    pmdcat_dataset.issued = dateutil.parser.isoparse(str(record["issued"]))
    pmdcat_dataset.modified = dateutil.parser.isoparse(str(record["modified"]))
    pmdcat_dataset.comment = _none_or_map(record.get("comment"), str)
    pmdcat_dataset.description = _none_or_map(record.get("description"), str)
    pmdcat_dataset.license = _none_or_map(record.get("license"), str)
    pmdcat_dataset.creator = _none_or_map(record.get("creator"), str)
    pmdcat_dataset.publisher = _none_or_map(record.get("publisher"), str)
    pmdcat_dataset.landing_page = (
        set()
        if len(str(record["landingPages"])) == 0
        else set(str(record["landingPages"]).split("|"))
    )
    pmdcat_dataset.themes = (
        set() if len(str(record["themes"])) == 0 else set(str(record["themes"]).split("|"))
    )
    pmdcat_dataset.keywords = (
        set()
        if len(str(record["keywords"])) == 0
        else set(str(record["keywords"]).split("|"))
    )
    pmdcat_dataset.contact_point = _none_or_map(record.get("contactPoint"), str)
    pmdcat_dataset.identifier = str(record.get("identifier"))
    dataset_contents_uri = str(record.get("datasetContents", record["dataset"]))
    pmdcat_dataset.dataset_contents = ExistingResource(dataset_contents_uri)

    return pmdcat_dataset


def _none_or_map(val: Optional[Any], map_func: Callable[[Any], Any]) -> Optional[Any]:
    if val is None:
        return None
    else:
        return map_func(val)


def _get_csv_cubed_output_type(csvw_rdf_graph: Graph) -> CsvCubedOutputType:
    is_concept_scheme = ask(
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

    is_qb_dataset = ask(
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
