import unittest
from typing import Dict, Any


from csvqb.models.cube import *
from csvqb.tests.unit.unittestbase import UnitTestBase
from csvqb.writers import skoscodelistwriter as codelistwriter

basic_code_list = NewQbCodeList(CatalogMetadata("Some CodeList"), [
    NewQbConcept("First Concept", code="1st-concept", description="This is the first concept."),
    NewQbConcept("Second Concept", parent_code="1st-concept", sort_order=20)
])


class CodeListWriterTests(UnitTestBase):

    def test_code_list_data_mapping(self):
        """
            Test that a `pd.DataFrame` containing the codes is correctly generated from a `NewQbCodeList`.
        """
        data = codelistwriter._get_code_list_data(basic_code_list)
        actual_column_names = list(data.columns)
        self.assertCountEqual(["Label", "Notation", "Parent Notation", "Sort Priority", "Description"],
                              actual_column_names)

        first_concept: Dict[str, Any] = data.iloc[[0]].to_dict("records")[0]
        self.assertEqual("First Concept", first_concept["Label"])
        self.assertEqual("1st-concept", first_concept["Notation"])
        self.assertIsNone(first_concept.get("Parent Notation"))
        self.assertEqual(0, first_concept["Sort Priority"])
        self.assertEqual("This is the first concept.", first_concept["Description"])

        second_concept: Dict[str, Any] = data.iloc[[1]].to_dict("records")[0]
        self.assertEqual("Second Concept", second_concept["Label"])
        self.assertEqual("second-concept", second_concept["Notation"])
        self.assertEqual("1st-concept", second_concept["Parent Notation"])
        self.assertEqual(20, second_concept["Sort Priority"])
        self.assertIsNone(second_concept.get("Description"))


if __name__ == "__main__":
    unittest.main()
