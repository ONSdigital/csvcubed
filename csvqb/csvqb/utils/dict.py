"""
Dictionary
----------
"""
from typing import Any, Optional, Callable, List, Dict
import rdflib
import json

from sharedmodels.rdf.resource import NewResource


def get_from_dict_ensure_exists(config: dict, key: str) -> Any:
    val = config.get(key)
    if val is None:
        raise Exception(f"Couldn't find value for key '{key}'")
    return val


def get_with_func_or_none(
    d: dict, prop_name: str, func: Callable[[Any], Any]
) -> Optional[Any]:
    return func(d[prop_name]) if d.get(prop_name) is not None else None


def rdf_resource_to_json_ld(resource: NewResource) -> List[Dict[str, Any]]:
    """
    Converts a `NewResource` RDF model into a list of dictionaries containing json-ld
    """
    g = rdflib.Graph()
    resource.to_graph(g)
    return json.loads(g.serialize(format="json-ld") or "[]")
