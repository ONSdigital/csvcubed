"""
CodeList
---------

Utilities for skos:codelists
"""

from enum import Enum
from typing import List, Optional

import numpy as np
import pandas as pd
from treelib import Tree

from csvcubed.models.csvcubedexception import (
    ErrorProcessingDataFrameException,
    InvalidNumberOfRecordsException,
    PrimaryKeyColumnTitleCannotBeNoneException,
)
from csvcubed.models.sparqlresults import ColumnDefinition


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
    columns: List[ColumnDefinition], property_url: CodelistPropertyUrl
) -> Optional[str]:
    """n
    Returns dataset column title for the given property url.

    Member of :class:`./codelist`.

    :return: `str` - dataset column title.
    """

    results = [
        column for column in columns if column.property_url == property_url.value
    ]

    if len(results) != 1:
        raise InvalidNumberOfRecordsException(
            record_description="code lists",
            excepted_num_of_records=1,
            num_of_records=len(results),
        )

    return results[0].title


def get_codelist_col_title_from_col_name(
    columns: List[ColumnDefinition], col_name: str
) -> str:
    """
    Returns the column title for the column name.

    Member of :class:`./codelist`.

    :return: `str` - dataset column title.
    """

    results = [column for column in columns if column.name == col_name]

    if len(results) != 1:
        raise InvalidNumberOfRecordsException(
            record_description="columns",
            excepted_num_of_records=1,
            num_of_records=len(results),
        )

    if results[0].title is None:
        raise PrimaryKeyColumnTitleCannotBeNoneException()

    return results[0].title


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

    # Replacing empty values with None.
    concepts_df_na_replaced = concepts_df.replace({np.nan: None})
    if concepts_df_na_replaced is None:
        raise ErrorProcessingDataFrameException(operation="replace")

    for _, concept_row in pd.DataFrame(concepts_df_na_replaced).iterrows():
        node_id = concept_row[notation_col_name]
        node_label = concept_row[label_col_name]
        node_parent_id = concept_row[parent_notation_col_name] or "root"
        tree.create_node(node_label, identifier=node_id, parent=node_parent_id)

    return tree
