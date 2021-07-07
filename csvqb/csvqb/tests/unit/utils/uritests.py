import unittest


from csvqb.tests.unit.unittestbase import UnitTestBase
from csvqb.utils.uri import get_last_uri_part, csvw_column_name_safe


class MyTestCase(UnitTestBase):
    def test_uri_last_part(self):
        self.assertEqual("dataset-name#something", get_last_uri_part("http://gss-data.org.uk/data/stuff/dataset-name#something"))

    def test_csvw_column_name(self):
        self.assertEqual("some_random_column_name", csvw_column_name_safe("Some Random Column //+Name"))
        self.assertEqual("something_else", csvw_column_name_safe("Something-else"))


if __name__ == '__main__':
    unittest.main()
