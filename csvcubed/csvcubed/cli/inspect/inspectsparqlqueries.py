"""
Inspect SPARQL Queries
----------------------

Collection of SPARQL queries used in the inspect cli.
"""

from typing import List

from rdflib import Graph
from rdflib.query import ResultRow

from csvcubed.utils.sparql import ask, select


def ask_is_csvw_code_list(rdf_graph: Graph) -> bool:
    """
    Queries whether the given rdf is a code list (i.e. skos:ConceptScheme).

    Member of :file:`./inspectsparqlqueries.py`

    :return: `bool` - Boolean specifying whether the rdf is code list (true) or not (false).
    """
    return ask(
        """
            ASK 
            WHERE {
                ?conceptScheme a <http://www.w3.org/2004/02/skos/core#ConceptScheme>.
            }
        """,
        rdf_graph,
    )


def ask_is_csvw_qb_dataset(rdf_graph: Graph) -> bool:
    """
    Queries whether the given rdf is a qb dataset (i.e. qb:Dataset).

    Member of :file:`./inspectsparqlqueries.py`

    :return: `bool` - Boolean specifying whether the rdf is code list (true) or not (false).
    """
    return ask(
        """
            ASK 
            WHERE {
                ?qbDataSet a <http://purl.org/linked-data/cube#DataSet>.
            }
        """,
        rdf_graph,
    )


def select_csvw_catalog_metadata(rdf_graph: Graph) -> ResultRow:
    """
    Queries catalog metadata such as title, label, issued date/time, modified data/time, etc.

    Member of :file:`./inspectsparqlqueries.py`

    :return: `List[ResultRow]` - List containing the results. The expected length of this list for this query is 1.
    """
    results: List[ResultRow] = select(
        """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
        SELECT ?dataset ?title ?label ?issued ?modified ?comment ?description ?license ?creator ?publisher 
            (GROUP_CONCAT(?landingPage ; separator='|') as ?landingPages) 
            (GROUP_CONCAT(?theme; separator='|') as ?themes) 
            (GROUP_CONCAT(?keyword; separator='|') as ?keywords) 
            ?contactPoint ?identifier
        WHERE {
            {
                SELECT DISTINCT ?dataset
                WHERE {
                    ?dataset a dcat:Dataset.        
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
        }
        """,
        rdf_graph,
    )

    if len(results) != 1:
        raise Exception(f"Expected 1 dcat:Dataset record, found {len(results)}")

    return results[0]


def select_csvw_dsd_dataset_label_and_dsd_def_uri(rdf_graph: Graph) -> ResultRow:
    """
    Queries data structure definition dataset label and uri.

    Member of :file:`./inspectsparqlqueries.py`

    :return: `List[ResultRow]` - List containing the results. The expected length of this list for this query is 1.
    """
    results: List[ResultRow] = select(
        """
        PREFIX qb: <http://purl.org/linked-data/cube#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT *
        WHERE {
            ?dataSet a qb:DataSet;
                rdfs:label ?dataSetLabel;
                qb:structure ?dataStructureDefinition.
        }
        """,
        rdf_graph,
    )

    if len(results) != 1:
        raise Exception(f"Expected 1 dcat:Dataset record, found {len(results)}")

    return results[0]


def select_csvw_dsd_qube_components(rdf_graph: Graph, dsd_uri: str) -> List[ResultRow]:
    """
    Queries the list of qube components.

    Member of :file:`./inspectsparqlqueries.py`

    :return: `List[ResultRow]` - List containing the results.
    """
    return select(
        f"""
        PREFIX qb: <http://purl.org/linked-data/cube#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX csvw: <http://www.w3.org/ns/csvw#>

        SELECT DISTINCT ?componentProperty ?componentPropertyLabel ?componentOrder ?componentPropertyType ?csvColumnTitle (?csvColumnRequired || ?componentRequired as ?required)
        WHERE {{   
            {{
                SELECT DISTINCT ?csvColumnTitle ?csvColumnRequired ?component ?componentProperty ?componentOrder 
                WHERE {{
                    <{dsd_uri}> qb:component ?component.
                    
                    ?component qb:componentProperty|qb:dimension|qb:measureDimension|qb:measure|qb:attribute ?componentProperty;
                            qb:order ?componentOrder.

                    OPTIONAL {{
                        {{
                            SELECT ?csvColumnTitle ?csvColumnPropertyUrl ?csvColumnRequired
                            WHERE {{
                                ?csvColumn csvw:propertyUrl ?csvColumnPropertyUrl;
                                        csvw:title ?csvColumnTitle.

                                {{
                                    ?csvColumn csvw:required ?csvColumnRequired.
                                }} UNION {{
                                    BIND(false as ?csvColumnRequired).
                                    FILTER NOT EXISTS {{
                                        ?csvColumn csvw:required ?csvColumnRequired.
                                    }}
                                }}

                            }}
                        }}

                        FILTER(STRENDS(str(?componentProperty), str(?csvColumnPropertyUrl))).
                    }}
                }}
            }}
            
            OPTIONAL {{
                ?componentProperty rdfs:label ?componentPropertyLabel.
            }}

            OPTIONAL {{
                # https://www.w3.org/TR/vocab-data-cube/#h3_reference-compspec
                {{
                    ?component qb:dimension ?dimension.
                    BIND (qb:DimensionProperty as ?componentPropertyType).
                    BIND (true as ?componentRequired)
                }} UNION {{
                    # https://www.w3.org/TR/vocab-data-cube/#dfn-qb-measuredimension
                    ?component qb:measureDimension ?dimension.
                    BIND (qb:MeasureProperty as ?componentPropertyType).
                    BIND (true as ?componentRequired)
                }} UNION {{
                    ?component qb:measure ?measure.
                    BIND (qb:MeasureProperty as ?componentPropertyType).
                    BIND (true as ?componentRequired)
                }} UNION {{
                    ?component qb:attribute ?attribute.
                    BIND (qb:AttributeProperty as ?componentPropertyType).

                    {{
                        ?component qb:componentRequired ?componentRequired.
                    }} UNION {{
                        BIND (false as ?componentRequired)
                        FILTER NOT EXISTS {{
                            ?component qb:componentRequired [].
                        }}
                    }}
                }}
            }}
        }}    
        ORDER BY ASC(?componentOrder)
        """,
        rdf_graph,
    )


def select_cols_w_supress_output(rdf_graph: Graph) -> List[ResultRow]:
    """
    Queries the columns with suppress output is true.

    Member of :file:`./inspectsparqlqueries.py`

    :return: `List[ResultRow]` - List containing the results.
    """
    return select(
        """
        PREFIX csvw: <http://www.w3.org/ns/csvw#>

        SELECT DISTINCT ?csvColumnTitle
        WHERE {
            ?csvColumn csvw:title ?csvColumnTitle;
                    csvw:suppressOutput true.
        }
        """,
        rdf_graph,
    )
