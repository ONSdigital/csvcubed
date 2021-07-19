"""
    Write `NewQbCodeList`s to CSV-Ws as `skos:ConceptScheme`s with DCAT2 metadata.
"""
import datetime
import json
from pathlib import Path
from typing import Tuple
import pandas as pd
from rdflib import FOAF, SKOS
from sharedmodels.rdf import dcat
from sharedmodels.rdf.resource import NewResourceWithType


from csvqb.models.cube.csvqb.components.codelist import NewQbCodeList
from csvqb.utils.dict import rdf_resource_to_json_ld_dict
from csvqb.models.rdf.conceptschemeincatalog import ConceptSchemeInCatalog


def _doc_rel_uri(fragment: str) -> str:
    return f"#{fragment}"


def new_code_list_to_csvw(new_code_list: NewQbCodeList, code_list_directory: Path) -> None:
    csv_file_name = f"{new_code_list.metadata.uri_safe_identifier}.csv"

    csv_file_path = (code_list_directory / csv_file_name).absolute()
    metadata_file_path = (code_list_directory / f"{csv_file_name}-metadata.json").absolute()

    csvw_metadata, data = _new_code_list_to_csvw_parts(new_code_list)

    with open(str(csv_file_path), "w+") as f:
        json.dump(csvw_metadata, f)

    data.to_csv(str(metadata_file_path), index=False)


def _new_code_list_to_csvw_parts(new_code_list: NewQbCodeList) -> Tuple[dict, pd.DataFrame]:
    csvw_metadata = _get_csvw_metadata(new_code_list)
    data = _get_code_list_data(new_code_list)

    return data, csvw_metadata


def _get_csvw_metadata(new_code_list: NewQbCodeList) -> dict:

    additional_metadata = _get_catalog_metadata(new_code_list)

    csvw_metadata = {
        "@context": "http://www.w3.org/ns/csvw",
        "@id": _doc_rel_uri("scheme"),
        "rdfs:label": new_code_list.metadata.title,
        "dct:title": new_code_list.metadata.title,
        "rdfs:seeAlso": rdf_resource_to_json_ld_dict(additional_metadata)
    }

    return csvw_metadata


def _get_catalog_metadata(new_code_list: NewQbCodeList) -> dcat.CatalogRecord:
    dt_now = datetime.datetime.now()
    metadata = new_code_list.metadata

    catalog_record = dcat.CatalogRecord(_doc_rel_uri("catalog-record"))
    catalog_record.label = catalog_record.title = metadata.title
    catalog_record.comment = catalog_record.description = metadata.description
    catalog_record.issued = catalog_record.modified = dt_now

    concept_scheme = catalog_record.primary_topic = ConceptSchemeInCatalog(_doc_rel_uri("scheme"))
    concept_scheme.label = concept_scheme.title = metadata.title
    concept_scheme.issued = metadata.issued or dt_now
    concept_scheme.modified = dt_now
    concept_scheme.comment = metadata.summary
    concept_scheme.description = metadata.description
    concept_scheme.license = metadata.license
    concept_scheme.publisher = metadata.publisher
    concept_scheme.landing_page = metadata.landing_page
    concept_scheme.themes = set(metadata.themes)
    concept_scheme.keywords = set(metadata.keywords)

    return catalog_record


def _get_code_list_data(new_code_list: NewQbCodeList) -> pd.DataFrame:
    return pd.DataFrame({
        "Label": [c.label for c in new_code_list.concepts],
        "Notation": [c.code for c in new_code_list.concepts],
        "Parent Notation": [c.parent_code for c in new_code_list.concepts],
        "Sort Priority": [c.sort_order or i for i, c in enumerate(new_code_list.concepts)],
        "Description": [c.description for c in new_code_list.concepts]
    })

