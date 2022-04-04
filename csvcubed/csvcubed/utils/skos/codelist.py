"""
CodeList
---------

Utilities for skos:codelists
"""

from enum import Enum
from typing import List, Optional
import pandas as pd
import numpy as np

from treelib import Tree

from csvcubed.models.inspectsparqlresults import CodelistColumnResult
from csvcubed.models.csvcubedexception import (
    ErrorProcessingDataFrameException,
    InvalidNumberOfRecordsException,
)


class CodelistPropertyUrl(Enum):
    """
    The codelist column property url types.
    """

    RDFLabel = "rdfs:label"

    SkosNotation = "skos:notation"

    SkosBroader = "skos:broader"

    SortPriority = "http://www.w3.org/ns/ui#sortPriority"

    RDFsComment = "rdfs:comment"

    SkosInScheme = "skos:inScheme"

    RDFType = "rdf:type"


def get_codelist_col_title_by_property_url(
    columns: List[CodelistColumnResult], property_url: CodelistPropertyUrl
) -> Optional[str]:
    """
    Returns dataset column title for the given property url.

    Member of :class:`./codelist`.

    :return: `str` - dataset column title.
    """
    results = [
        column for column in columns if column.column_property_url == property_url.value
    ]

    if len(results) != 1:
        raise InvalidNumberOfRecordsException(
            excepted_num_of_records=1, num_of_records=len(results)
        )

    return results[0].column_title


def build_concepts_hierarchy_tree(
    concepts_df: pd.DataFrame,
    parent_notation_col_name: str,
    label_col_name: str,
    notation_col_name: str,
) -> Tree:
    """
    Builds the concepts hierarchy as a tree data structure.

    Member of :class:`./codelist`.

    :return: `Tree` - concepts as a tree data structure.
    """

    tree = Tree()
    tree.create_node("root", identifier="root")

    # Replacing empty values with None and sorting consepts by Sort Priortiy to maintain the order when iterating below.
    concepts_df_na_replaced = concepts_df.replace({np.nan: None})
    if concepts_df_na_replaced is None:
        raise ErrorProcessingDataFrameException(operation="replace")

    concepts_df_sorted = pd.DataFrame(concepts_df_na_replaced).sort_values(
        by="Sort Priority"
    )
    if concepts_df_sorted is None:
        raise ErrorProcessingDataFrameException(operation="sort")

    for _, concept_row in pd.DataFrame(concepts_df_sorted).iterrows():
        node_id = concept_row[notation_col_name]
        node_label = concept_row[label_col_name]
        node_parent_id = concept_row[parent_notation_col_name] or "root"
        tree.create_node(node_label, identifier=node_id, parent=node_parent_id)

    return tree
