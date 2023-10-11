import json
from copy import deepcopy
from pathlib import Path

from rdflib import Graph
from rdflib.plugins.shared.jsonld.context import Context

from csvcubed.utils.uri import uri_safe


def _add_type_to_node(node: dict, additional_type: str) -> None:
    # Add a type to a JSON-LD node.
    # We don't overwrite any other types the user wanted to specify.
    existing_type = node.get("@type")
    if existing_type is None:
        new_type = additional_type
    elif isinstance(existing_type, list):
        # e.g. ["dcat:Dataset"]
        new_type = deepcopy(existing_type)
        new_type.append(additional_type)
    elif isinstance(existing_type, str):
        # e.g. "dcat:Dataset"
        new_type = [existing_type, additional_type]
    else:
        raise ValueError(f"Unhandled `@type` value '{existing_type}'")

    node["@type"] = new_type


def _set_concept_identifiers(concept: dict) -> None:
    # todo: This isn't the right identifier, we need to use uri_safe_identifier for each of the `NewQbConcept`s we generated to reliably identify the concepts.
    concept["@id"] = (
        "http://example.com/concept-scheme/this-one/concepts/" + concept["notation"]
    )
    _add_type_to_node(concept, "skos:Concept")
    for child_concept in concept.get("children", []):
        _set_concept_identifiers(child_concept)


codelist_config_path = Path("488-codelist-jsonld/new/codelist_config.jsonld")
codelist_context_path = Path("488-codelist-jsonld/new/codelist_context.json")

with open(codelist_config_path, "r") as f:
    config = json.load(f)

with open(codelist_context_path, "r") as f:
    ctx = json.load(f)

config["@id"] = uri_safe(config["title"]) + "#code-list"
_add_type_to_node(config, "dcat:Dataset")
_add_type_to_node(config, "skos:ConceptScheme")

for concept in config["concepts"]:
    _set_concept_identifiers(concept)

context = Context(ctx)
graph = Graph()
graph.parse(data=config, format="json-ld")
print(graph.serialize("488-codelist-jsonld/new/codelist.jsonld", format="json-ld"))
