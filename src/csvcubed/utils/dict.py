"""
Dictionary
----------

Functions to help when working with dictionaries.
"""
import logging
from typing import Any, Optional, Callable, List, Dict
import rdflib
import json

from csvcubedmodels.rdf.resource import NewResource


_logger = logging.getLogger(__name__)


def get_from_dict_ensure_exists(config: dict, key: str) -> Any:
    """
    Provides a more user-friendly error message when it cannot find the :obj:`key` in :obj:`config`.

    :return: :obj:`config` [:obj:`key`]

    :raises Exception: when :obj:`key` cannot be found in :obj:`config`.
    """
    val = config.get(key)
    if val is None:
        raise Exception(f"Couldn't find value for key '{key}'")
    return val


def get_with_func_or_none(
    d: dict, prop_name: str, func: Callable[[Any], Any]
) -> Optional[Any]:
    """
    Applies :func:`func` to the value of :obj:`d` [:obj:`prop_name`] if it exists and returns the result.

    :return: `func(d[prop_name])` OR :obj:`None`.
    """
    return func(d[prop_name]) if d.get(prop_name) is not None else None


def rdf_resource_to_json_ld(resource: NewResource) -> List[Dict[str, Any]]:
    """
    Converts a :class:`~csvcubedmodels.rdf.resource.NewResource` RDF model into a list of dictionaries containing json-ld
    """
    g = rdflib.Graph()
    resource.to_graph(g)
    json_ld = g.serialize(format="json-ld") or "[]"
    _logger.debug("Serialised RDF Graph to JSON-LD: %s", json_ld)
    return json.loads(json_ld)
