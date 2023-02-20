"""
SKOS Codelist Reader
--------------------

Read some information from a CSV-W `skos:ConceptScheme`.
"""
import logging
import re
from pathlib import Path
from typing import Set, Tuple

from uritemplate import variables

from csvcubed.utils.iterables import first
from csvcubed.utils.sparql_handler.code_list_inspector import CodeListInspector
from csvcubed.utils.tableschema import CsvWRdfManager

_logger = logging.getLogger(__name__)


def extract_code_list_concept_scheme_info(
    code_list_csvw_path: Path,
) -> Tuple[str, str, str]:
    """
    :return: the (:obj:`csv_url_or_relative_path`, :obj:`concept_scheme_uri`, :obj:`concept_uri_template`) from a
      CSV-W representing a `skos:ConceptScheme`.

      `concept_uri_template` uses the standard `notation` uri template variable even if the underlying file uses a
       different column name.
    """

    csvw_rdf_manager = CsvWRdfManager(code_list_csvw_path)
    csvw_inspector = csvw_rdf_manager.csvw_inspector
    concept_scheme_uri = csvw_inspector.get_primary_catalog_metadata().dataset_uri
    csv_url = (
        CodeListInspector(csvw_inspector)
        .get_table_identifiers_for_concept_scheme(concept_scheme_uri)
        .csv_url
    )
    # csvw_inspector.identifiers
    result = csvw_inspector.get_table_info_for_csv_url(csv_url)

    about_url = result.about_url
    table_url = result.csv_url

    variables_in_about_url: Set[str] = {v for v in variables(about_url)}
    if len(variables_in_about_url) != 1:
        raise ValueError(
            "Unexpected number of variables in aboutUrl Template. "
            + f"Expected 1, found {len(variables_in_about_url)}"
        )

    variable_name_in_about_url = first(variables_in_about_url)
    if variable_name_in_about_url is None:
        raise ValueError("Variable name in about url cannot be none")

    if variable_name_in_about_url != "notation":
        _logger.debug(
            'Replacing variable name "%s" in URI template with "notation" for consistency.',
            variable_name_in_about_url,
        )
        about_url = re.sub(
            "\\{(.?)" + re.escape(variable_name_in_about_url) + "\\}",
            "{\\1notation}",
            about_url,
        )
    return table_url, concept_scheme_uri, about_url
