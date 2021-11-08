"""
Date-Time Code List Generation
------------------------------
"""
import json
import re
from pathlib import Path
import pandas as pd
from csvcubed.models.rdf.conceptschemeincatalog import ConceptSchemeInCatalog
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.utils.dict import rdf_resource_to_json_ld
from rdflib import Graph
from typing import List, Tuple, Any, Dict, Set, Optional
import csvw
from uritemplate import expand

from csvcubedpmd.models.csvwithcolumndefinitions import CsvWithColumnDefinitions


def generate_date_time_code_lists_for_csvw_metadata_file(
    metadata_file: Path, output_directory: Optional[Path] = None
) -> List[Path]:
    output_directory = output_directory or metadata_file.parent
    date_time_dimensions = _get_dimensions_to_generate_code_lists_for(metadata_file)
    files_created: List[Path] = []
    for (dimension, label, code_list_uri) in date_time_dimensions:
        file_created = _create_code_list_for_dimension(
            metadata_file, dimension, label, code_list_uri, output_directory
        )
        files_created.append(file_created)

    return files_created


def _get_dimensions_to_generate_code_lists_for(
    csv_metadata_file: Path,
) -> List[Tuple[str, str, Optional[str]]]:
    metadata_graph = Graph().parse(str(csv_metadata_file), format="json-ld")

    result = metadata_graph.query(
        """
        PREFIX qb: <http://purl.org/linked-data/cube#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX sdmxd:  <http://purl.org/linked-data/sdmx/2009/dimension#>
        
        SELECT DISTINCT ?dimension ?dimensionLabel ?codeList
        WHERE {
           [] a qb:DataSet;
              qb:structure/qb:component/qb:dimension ?dimension.
          
          ?dimension 
            rdfs:subPropertyOf sdmxd:refPeriod;
            rdfs:label ?dimensionLabel.
          OPTIONAL { ?dimension qb:codeList ?codeList. } 
        }    
    """
    )
    return [
        (str(dim), str(label), None if code_list is None else str(code_list))
        for dim, label, code_list in result
    ]


def _get_csv_columns_for_dimension(
    csv_metadata_file: Path, dimension: str
) -> Dict[CsvWithColumnDefinitions, List[str]]:
    """
    Return the CSV file URLs with column numbers which contain values in a given dimension (URI).

    N.B. the index is zero-based.
    :param csv_metadata_file:
    :param dimension:
    :return:
    """
    table_group = csvw.TableGroup.from_file(csv_metadata_file)
    tables = table_group.tables
    assert isinstance(tables, list)
    map_path_to_csv_mapping: Dict[Path, CsvWithColumnDefinitions] = {}
    map_csv_to_column_names: Dict[CsvWithColumnDefinitions, List[str]] = {}

    for table in tables:
        assert isinstance(table, csvw.Table)
        # N.B. this assumes that the CSV file is located relative to the metadata file.
        # This doesn't work if the CSV is specified as a URL.
        csv_path = csv_metadata_file.parent / Path(str(table.url))
        schema = table.tableSchema
        assert isinstance(schema, csvw.metadata.Schema)
        columns = schema.columns
        assert isinstance(columns, list)
        for column in columns:
            assert isinstance(column, csvw.Column)
            if column.propertyUrl == dimension and not column.virtual:
                if csv_path not in map_path_to_csv_mapping:
                    csv_file_info = CsvWithColumnDefinitions(csv_path, columns)

                    map_path_to_csv_mapping[csv_path] = csv_file_info
                    map_csv_to_column_names[csv_file_info] = []

                csv_mappings = map_path_to_csv_mapping[csv_path]

                map_csv_to_column_names[csv_mappings].append(str(column.name))

    return map_csv_to_column_names


def _get_unique_values_from_columns(
    csv_col_mappings: Dict[CsvWithColumnDefinitions, List[str]]
) -> Set[Any]:
    unique_values: Set[Any] = set()
    for csv in csv_col_mappings.keys():
        data = pd.read_csv(csv.csv_path)
        assert isinstance(data, pd.DataFrame)
        column_names_with_values = csv_col_mappings[csv]
        columns_with_values = [
            col for col in csv.columns if col.name in column_names_with_values
        ]

        # Rename column headers to match the CSV-W's `name` property to make lookup easier.
        data.columns = pd.Index([col.name for col in csv.columns if not col.virtual])

        for row_tuple in data.itertuples():
            row = row_tuple._asdict()  # type: ignore
            for column in columns_with_values:
                column_value_for_row = expand(str(column.valueUrl), row)
                unique_values.add(column_value_for_row)
    return unique_values


def _create_code_list_for_dimension(
    csv_metadata_file: Path,
    dimension_uri: str,
    label: str,
    code_list_uri: Optional[str],
    output_directory: Path,
) -> Path:
    """
    :return: :obj:`~pathlib.Path` of the CSV-Metadata file generated.
    """
    columns = _get_csv_columns_for_dimension(csv_metadata_file, dimension_uri)
    unique_values = _get_unique_values_from_columns(columns)

    code_list_csv_file_name = re.sub("[^A-Za-z0-9]+", "-", label) + ".csv"
    code_list_metadata_file_name = f"{code_list_csv_file_name}-metadata.json"

    code_list_metadata = _generate_date_time_code_list_metadata(
        code_list_csv_file_name, code_list_uri, label
    )

    code_list_data = pd.DataFrame(
        {
            "URI": list(sorted(unique_values)),
            "Sort Priority": range(0, len(unique_values)),
        }
    )

    code_list_metadata_out = output_directory / code_list_metadata_file_name
    code_list_csv_out = output_directory / code_list_csv_file_name

    with open(code_list_metadata_out, "w+") as f:
        json.dump(code_list_metadata, f, indent=4)

    code_list_data.to_csv(code_list_csv_out, index=False)

    return code_list_metadata_out


"""
TODO: What am I going to do about date-time code-lists?

Do they need to move into csvcubed or should they remain here and go back and update the model in the qb CSV-W?

I think they need to be moved to csvcubed, but we need a bit more thought in that direction.

"""


def _generate_date_time_code_list_metadata(
    code_list_csv_file_name: str, code_list_uri: Optional[str], label: str
) -> dict:
    # If the code_list_uri is specified, it has been defined in the qb
    code_list_uri = code_list_uri or f"{code_list_csv_file_name}#scheme"
    code_list_metadata = {
        "@context": "http://www.w3.org/ns/csvw",
        "url": code_list_csv_file_name,
        "tableSchema": {
            "columns": [
                {"titles": "URI", "name": "uri", "suppressOutput": True},
                {
                    "titles": "Sort Priority",
                    "name": "sort_priority",
                    "datatype": "integer",
                    "propertyUrl": "http://www.w3.org/ns/ui#sortPriority",
                },
                {
                    "virtual": True,
                    "propertyUrl": "rdf:type",
                    "valueUrl": "skos:Concept",
                },
                {
                    "virtual": True,
                    "propertyUrl": "skos:inScheme",
                    "valueUrl": code_list_uri,
                },
                {
                    "virtual": True,
                    "aboutUrl": code_list_uri,
                    "propertyUrl": "skos:hasTopConcept",
                    "valueUrl": "{+uri}",
                },
            ],
            "aboutUrl": "{+uri}",
        },
    }
    generic_comment = f"{label} code list containing date/time concepts."

    catalog_metadata = CatalogMetadata(
        title=label, summary=generic_comment, description=generic_comment
    )

    concept_scheme_with_metadata = ConceptSchemeInCatalog(code_list_uri)
    catalog_metadata.configure_dcat_dataset(concept_scheme_with_metadata)

    code_list_metadata["rdfs:seeAlso"] = rdf_resource_to_json_ld(
        concept_scheme_with_metadata
    )

    return code_list_metadata
