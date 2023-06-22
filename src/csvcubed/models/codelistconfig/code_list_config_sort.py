"""
Code List Config Sort
----------------

Models for sorting code lists.
"""

from dataclasses import dataclass
from typing import Any, Set

from csvcubedmodels.dataclassbase import DataClassBase


@dataclass
class CodeListConfigSort(DataClassBase):
    """Model for representing the sort object in code list config."""

    by: str
    method: str


def sort_concepts(concepts: Any, sort: Any):
    """
    Sorting concepts based on the sort object and sort order defined in the code list json.
    """
    # Step 1: Identify sort orders defined by the user in code list config json.
    user_defined_sort_orders: Set[int] = {
        concept.sort_order for concept in concepts if concept.sort_order is not None
    }

    # Step 2: Identify the concepts with and without sort order.
    concepts_with_sort_order = [
        concept for concept in concepts if concept.sort_order is not None
    ]
    concepts_without_sort_order = [
        concept for concept in concepts if concept.sort_order is None
    ]

    # Step 3: If the sort object is defined, concepts without a sort order will be sorted by the sort object first.
    if sort is not None:
        if sort.by != "label" and sort.by != "notation":
            raise ValueError(
                f"Unsupported sort by {sort.by}. The supported options are 'label' and 'notation'."
            )
        if sort.method != "ascending" and sort.by != "descending":
            raise ValueError(
                f"Unsupported sort method {sort.method}. The supported options are 'ascending' and 'descending'."
            )

        concepts_without_sort_order.sort(
            key=lambda concept: (
                concept.label if sort and sort.by == "label" else concept.notation,
            ),
            reverse=True if sort.method == "descending" else False,
        )

    # Step 4: Fianlly, all the concepts are sorted by the sort order.
    all_concepts = concepts_with_sort_order + assign_sort_order_to_concepts(
        concepts_without_sort_order, user_defined_sort_orders
    )

    sorted_concepts = sorted(
        all_concepts,
        key=lambda concept: concept.sort_order is not None and concept.sort_order,
        reverse=False,
    )

    return sorted_concepts


def assign_sort_order_to_concepts(
    concepts_without_sort_order: Any,
    user_defined_sort_orders: Set[int],
):
    """Assinging a sort order to concepts without sort order whilst avoiding conflicts with the sort orders already used by the user."""

    sort_order: int = 0
    concepts = []
    for concept in concepts_without_sort_order:
        while sort_order in user_defined_sort_orders:
            sort_order += 1
        concept.sort_order = sort_order
        concepts.append(concept)
        sort_order += 1

    return concepts


def apply_sort_to_child_concepts(
    concepts: Any,
    config: Any,
):
    """
    Sorting children in each parent concept seperately.
    """
    for concept in concepts:
        if any(concept.children):
            concept.children = sort_concepts(concept.children, config.sort)
            apply_sort_to_child_concepts(concept.children, config)
