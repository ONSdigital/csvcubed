"""
CodeList
-----------

Utilities for skos:codelists
"""

from enum import Enum
from typing import List
import pandas as pd

from treelib import Node, Tree

from csvcubed.models.inspectsparqlresults import CodelistColumnResult


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


def get_codelist_col_title_by_property_uri(
    columns: List[CodelistColumnResult], property_url: CodelistPropertyUrl
) -> str:
    return [column for column in columns if column.column_property_url == property_url]


def build_codelist_hierarchy_tree(
    concepts_df: pd.DataFrame,
    parent_notation_col: str,
    label_col: str,
    notation_col: str,
) -> Tree:
    tree = Tree()
    tree.create_node("root", identifier="root")
    tree.create_node("Jane", identifier="jane", parent="root")
    tree.create_node("Bill", identifier="bill", parent="root")
    tree.create_node("Diane", identifier="diane", parent="root")
    tree.create_node("Mary", identifier="mary", parent="root")
    tree.create_node("Mark", identifier="mark", parent="root")

    return tree
