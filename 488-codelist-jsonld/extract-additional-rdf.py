from copy import deepcopy
from json import load
from pathlib import Path

import rdflib
from csvcubedmodels.rdf import RDF, SKOS

# code_list_json_path = Path("488-codelist-jsonld/json-ld/config-context-dict.json")

code_list_json_path = Path("488-codelist-jsonld/json-ld/config-context-str.json")

# code_list_json_path = Path("488-codelist-jsonld/json-ld/config-context-list.json")

# code_list_json_path = Path("488-codelist-jsonld/json-ld/config-no-context.json")


def _override_context(node: dict, overrides: dict) -> None:
    # Add our context overrides to the document's context so that we only project out the information we haven't already extracted.
    existing_context = node.get("@context")

    if existing_context is None:
        new_context = deepcopy(overrides)
        # Need to make sure that the standard prefixes are available.
        new_context["@import"] = "http://www.w3.org/2013/json-ld-context/rdfa11"
    elif isinstance(existing_context, list):
        # e.g. ["./code-list.jsonld", {"@language": "en"}]
        new_context = deepcopy(existing_context)
        new_context[1] = new_context[1].update(**deepcopy(overrides))
    elif isinstance(existing_context, str):
        # e.g. "./code-list.jsonld"
        new_context = [existing_context, deepcopy(overrides)]
    elif isinstance(existing_context, dict):
        # e.g. "@language": "en"}
        new_context = deepcopy(existing_context).update(**deepcopy(overrides))
    else:
        raise ValueError(f"Unhandled `@context` value '{existing_context}'")

    node["@context"] = new_context


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


with open(code_list_json_path, "r") as f:
    code_list_json = load(f)

# Override all the fields we know will be in the JSON structure that we've already extracted.
# We're only interested in any additional information the user has provided us (and which concept it's part of).
# N.B. This would need to be kept in-sync with any changes made to the code-list-config.json syntax.
context_overrides = {
    "$schema": None,
    "id": None,
    "title": None,
    "description": None,
    "summary": None,
    "creator": None,
    "publisher": None,
    "dataset_issued": None,
    "dataset_modified": None,
    "license": None,
    "themes": None,
    "keywords": None,
    "sort": None,
    "concepts": {
        "@id": "skos:hasTopConcept",
        "@container": "@set",
        "@type": "skos:Concept",
        "@context": {
            "label": None,
            "notation": None,
            "same_as": None,
            "description": None,
            "sort_order": None,
            "concepts": {
                "@id": "skos:narrower",
                "@type": "skos:Concept",
                "@container": "@set",
            },
        },
    },
}

code_list_json["@id"] = "http://example.com/concept-scheme/this-one"
_override_context(code_list_json, context_overrides)
_add_type_to_node(code_list_json, "skos:ConceptScheme")


def _set_concept_identifiers(concept: dict) -> None:
    # todo: This isn't the right identifier, we need to use uri_safe_identifier for each of the `NewQbConcept`s we generated to reliably identify the concepts.
    concept["@id"] = (
        "http://example.com/concept-scheme/this-one/concepts/" + concept["notation"]
    )
    _add_type_to_node(concept, "skos:Concept")
    for child_concept in concept.get("concepts", []):
        _set_concept_identifiers(child_concept)


for concept in code_list_json["concepts"]:
    _set_concept_identifiers(concept)

graph = rdflib.Graph()
graph.parse(data=code_list_json, format="json-ld")
# Get rid of the now-unnecessary scaffolding.
# This means we're genuinely left with the additional information the user wanted to add.
print(f"\nConfig: {code_list_json_path}\n")
print(graph.serialize(format="ttl"))
graph.remove((None, RDF.type, SKOS.ConceptScheme))
graph.remove((None, SKOS.hasTopConcept, None))
graph.remove((None, RDF.type, SKOS.Concept))
graph.remove((None, SKOS.narrower, None))
# Now we can print the RDF expressing just the additional RDF the user set.
print("Additional RDF:")
print(graph.serialize(format="ttl"))
