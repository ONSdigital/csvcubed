"""
URI Safe Validations
--------------------
"""
from typing import Tuple, List, Dict, Set, Type, Union

from csvcubed.models.cube.qb.components.validationerrors import (
    ConflictingUriSafeValuesError,
)


def ensure_no_uri_safe_conflicts(
    label_with_uri_safe_identifier: List[Tuple[str, str]],
    location: Union[Type, str],
) -> None:
    """
    Accepts a list of tuples of `(label, uri_safe_identifier)` and identifies any duplicate mappings of
    `label` => `uri_safe_identifier`.

    :raises ConflictingUriSafeValuesError when conflicts are found.
    """

    map_uri_safe_val_to_labels: Dict[str, Set[str]] = {}

    for (label, uri_safe_identifier) in label_with_uri_safe_identifier:
        labels_for_this_uri_safe_identifier = map_uri_safe_val_to_labels.get(
            uri_safe_identifier, set()
        )
        labels_for_this_uri_safe_identifier.add(label)
        map_uri_safe_val_to_labels[
            uri_safe_identifier
        ] = labels_for_this_uri_safe_identifier

    collisions = {
        uri_safe_value: labels
        for uri_safe_value, labels in map_uri_safe_val_to_labels.items()
        if len(labels) > 1
    }

    if any(collisions):
        raise ConflictingUriSafeValuesError(location, collisions)
