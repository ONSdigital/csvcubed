import pytest

from csvqb.models.cube import *


def test_basic_cube_metadata_validation():
    invalid_catalog_metadata = CatalogMetadata(title=None)
    errors = invalid_catalog_metadata.pydantic_validation()
    assert len(errors) == 1, print(", ".join([e.message for e in errors]))
    error = errors[0]
    assert "none is not an allowed value" in error.message
    assert "title" in error.message


if __name__ == "__main__":
    pytest.main()
