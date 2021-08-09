"""
Test adding Arbitrary RDF relations to a model.
"""

from dataclasses import dataclass, field
from typing import Set

import pytest
from rdflib import RDFS, FOAF
from rdflib.term import Identifier, URIRef, Literal
from sharedmodels.rdf import NewResource, InversePredicate

from csvqb.models.cube.csvqb.components.arbitraryrdfrelations import (
    ArbitraryRdfRelations,
    TripleFragmentBase,
    ResourceSerialisationHint,
    TripleFragment,
    InverseTripleFragment,
)


@dataclass
class SomeQbComponent(ArbitraryRdfRelations):
    arbitrary_rdf: Set[TripleFragmentBase] = field(default_factory=set)

    def get_permitted_rdf_fragment_hints(self) -> Set[ResourceSerialisationHint]:
        return {
            ResourceSerialisationHint.DefaultNode,
            ResourceSerialisationHint.Component,
        }


class AResource(NewResource):
    def __init__(self, uri: str):
        NewResource.__init__(self, uri)


class AComponent(NewResource):
    def __init__(self, uri: str):
        NewResource.__init__(self, uri)


def test_triple_fragment_serialised():
    """
    Test that triple fragments are correctly mapped to resources.
    """
    a = SomeQbComponent(
        arbitrary_rdf={
            TripleFragment("rdfs:label", "Some Default Node Label"),
            TripleFragment(
                "rdfs:label",
                "Some Component Label",
                ResourceSerialisationHint.Component,
            ),
        }
    )

    a_resource = AResource("http://some-resource")
    a_component = AComponent("http://some-component-resource")

    a.copy_arbitrary_triple_fragments_to_resources(
        {
            ResourceSerialisationHint.DefaultNode: a_resource,
            ResourceSerialisationHint.Component: a_component,
        }
    )

    assert (
        URIRef("rdfs:label"),
        Identifier("Some Default Node Label"),
    ) in a_resource.additional_rdf.items()
    assert (
        URIRef("rdfs:label"),
        Identifier("Some Component Label"),
    ) in a_component.additional_rdf.items()


def test_inverse_triple_fragment_serialised():
    """
    Test that *inverse* triple fragments are correctly mapped to resources.
    """
    a = SomeQbComponent(
        arbitrary_rdf={
            InverseTripleFragment(
                FOAF.primaryTopic, "http://resource-with-primary-contents"
            ),
        }
    )

    a_resource = AResource("http://some-resource")

    a.copy_arbitrary_triple_fragments_to_resources(
        {ResourceSerialisationHint.DefaultNode: a_resource}
    )

    assert (
        InversePredicate(FOAF.primaryTopic),
        URIRef("http://resource-with-primary-contents"),
    ) in a_resource.additional_rdf.items()


def test_hint_not_permitted_exception():
    """
    Ensure that when the user specifies a `ResourceSerialisationHint` which is not in the list of those permitted that
    they get a suitable exception.
    """
    a = SomeQbComponent(
        arbitrary_rdf={
            TripleFragment(
                "rdfs:label", "Some Label", ResourceSerialisationHint.Property
            ),
        }
    )

    a_resource = AResource("http://some-resource")

    with pytest.raises(Exception) as ex:
        a.copy_arbitrary_triple_fragments_to_resources(
            {ResourceSerialisationHint.DefaultNode: a_resource}
        )
    assert "not permitted" in str(ex)


def test_hint_not_mapped_exception():
    """
    Test that we get a suitable error where a hint is permitted but hasn't been mapped to a `NewResource`
    """
    a = SomeQbComponent(
        arbitrary_rdf={
            TripleFragment(
                "rdfs:label", "Some Label", ResourceSerialisationHint.Component
            ),
        }
    )

    a_resource = AResource("http://some-resource")

    with pytest.raises(Exception) as ex:
        a.copy_arbitrary_triple_fragments_to_resources(
            {ResourceSerialisationHint.DefaultNode: a_resource}
        )
    assert "Unhandled fragment hint type" in str(ex)


def test_rdflib_identifier_supported():
    """
    Ensure that when the user specifies a `ResourceSerialisationHint` which is not in the list of those permitted that
    they get a suitable exception.
    """
    a = SomeQbComponent(
        arbitrary_rdf={
            TripleFragment(RDFS.label, Literal("Rhywbeth neis iawn", "cy")),
            InverseTripleFragment(
                RDFS.subPropertyOf, URIRef("http://some-child-resource")
            ),
        }
    )

    a_resource = AResource("http://some-resource")

    a.copy_arbitrary_triple_fragments_to_resources(
        {ResourceSerialisationHint.DefaultNode: a_resource}
    )

    assert (
        RDFS.label,
        Literal("Rhywbeth neis iawn", "cy"),
    ) in a_resource.additional_rdf.items()
    assert (
        InversePredicate(RDFS.subPropertyOf),
        URIRef("http://some-child-resource"),
    ) in a_resource.additional_rdf.items()


if __name__ == "__main__":
    pytest.main()
