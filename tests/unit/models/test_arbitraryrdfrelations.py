"""
Test adding Arbitrary RDF relations to a model.
"""

from dataclasses import dataclass, field
from typing import List, Set

import pytest
from csvcubedmodels.rdf import InversePredicate, NewResource
from rdflib import FOAF, RDFS
from rdflib.term import Literal, URIRef

from csvcubed.models.cube.qb.components.arbitraryrdf import (
    ArbitraryRdf,
    InverseTripleFragment,
    RdfSerialisationHint,
    TripleFragment,
    TripleFragmentBase,
)


@dataclass
class SomeQbComponent(ArbitraryRdf):
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list)

    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        return self.arbitrary_rdf

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.Property

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {RdfSerialisationHint.Component, RdfSerialisationHint.Property}


class AProperty(NewResource):
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
        arbitrary_rdf=[
            TripleFragment("rdfs:label", "Some Default Property Label"),
            TripleFragment(
                "rdfs:label",
                "Some Component Label",
                RdfSerialisationHint.Component,
            ),
        ]
    )

    a_property = AProperty("http://some-resource-property")
    a_component = AComponent("http://some-component-resource")

    a.copy_arbitrary_triple_fragments_to_resources(
        {
            RdfSerialisationHint.Property: a_property,
            RdfSerialisationHint.Component: a_component,
        }
    )

    assert (
        URIRef("rdfs:label"),
        Literal("Some Default Property Label"),
    ) in a_property.additional_rdf
    assert (
        URIRef("rdfs:label"),
        Literal("Some Component Label"),
    ) in a_component.additional_rdf


def test_inverse_triple_fragment_serialised():
    """
    Test that *inverse* triple fragments are correctly mapped to resources.
    """
    a = SomeQbComponent(
        arbitrary_rdf=[
            InverseTripleFragment(
                FOAF.primaryTopic, "http://resource-with-primary-contents"
            ),
        ]
    )

    a_property = AProperty("http://some-resource")

    a.copy_arbitrary_triple_fragments_to_resources(
        {RdfSerialisationHint.Property: a_property}
    )

    assert (
        InversePredicate(FOAF.primaryTopic),
        URIRef("http://resource-with-primary-contents"),
    ) in a_property.additional_rdf


def test_hint_not_permitted_exception():
    """
    Ensure that when the user specifies a `ResourceSerialisationHint` which is not in the list of those permitted that
    they get a suitable exception.
    """
    a = SomeQbComponent(
        arbitrary_rdf={
            TripleFragment("rdfs:label", "Some Label", RdfSerialisationHint.Unit),
        }
    )

    a_property = AProperty("http://some-resource")

    with pytest.raises(Exception) as ex:
        a.copy_arbitrary_triple_fragments_to_resources(
            {RdfSerialisationHint.Property: a_property}
        )
    assert "not permitted" in str(ex)


def test_hint_not_mapped_exception():
    """
    Test that we get a suitable error where a hint is permitted but hasn't been mapped to a `NewResource`
    """
    a = SomeQbComponent(
        arbitrary_rdf=[
            TripleFragment("rdfs:label", "Some Label", RdfSerialisationHint.Component),
        ]
    )

    a_property = AProperty("http://some-resource")

    with pytest.raises(Exception) as ex:
        a.copy_arbitrary_triple_fragments_to_resources(
            {RdfSerialisationHint.Property: a_property}
        )
    assert "Unhandled fragment hint type" in str(ex)


def test_rdflib_identifier_supported():
    """
    Ensure that when the user specifies a `ResourceSerialisationHint` which is not in the list of those permitted that
    they get a suitable exception.
    """
    a = SomeQbComponent(
        arbitrary_rdf=[
            TripleFragment(RDFS.label, Literal("Rhywbeth neis iawn", "cy")),
            InverseTripleFragment(
                RDFS.subPropertyOf, URIRef("http://some-child-resource")
            ),
        ]
    )

    a_property = AProperty("http://some-resource")

    a.copy_arbitrary_triple_fragments_to_resources(
        {RdfSerialisationHint.Property: a_property}
    )

    assert (
        RDFS.label,
        Literal("Rhywbeth neis iawn", "cy"),
    ) in a_property.additional_rdf
    assert (
        InversePredicate(RDFS.subPropertyOf),
        URIRef("http://some-child-resource"),
    ) in a_property.additional_rdf


if __name__ == "__main__":
    pytest.main()
