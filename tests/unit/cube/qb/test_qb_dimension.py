import pandas as pd

from csvcubed.models.cube.qb.components import NewQbCodeList, NewQbDimension


def test_newqbdimension_extracts_newqbcodelist_newqbconcept():
    """
    To test a NewQbDimension correctly extracts and creates a valid NewQbCodeList & NewQbConcept
    """
    # New dimension with some repeated & distinct values
    data = pd.DataFrame({"New Dimension": ["A", "A", "C", "D", "E", "G", "G"]})

    new_dimension = NewQbDimension.from_data("Some Dataset", data["New Dimension"])

    # To see if there is a code_list for the new_dimension and is of type NewQbCodeList
    assert new_dimension.code_list is not None
    assert isinstance(new_dimension.code_list, NewQbCodeList)

    # Length of the concept list equals to number of distinct values in the data provided
    assert len(new_dimension.code_list.concepts) == 5

    # List of concept labels are asserted Individually
    concept_labels = [c.label for c in new_dimension.code_list.concepts]
    assert "A" in concept_labels
    assert "C" in concept_labels
    assert "D" in concept_labels
    assert "E" in concept_labels
    assert "G" in concept_labels

    # assert parent is None for distinct list of concepts
    parent_code_list = [c.parent_code for c in new_dimension.code_list.concepts]
    assert not any(parent_code_list)

    # assert if all the concept label is converted into something that can be used in a URI path segment (pathify).
    code = [c.code for c in new_dimension.code_list.concepts]
    assert "a" in code
    assert "c" in code
    assert "d" in code
    assert "e" in code
    assert "g" in code
