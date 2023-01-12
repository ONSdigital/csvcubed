import pytest

from csvcubed.models.cube.qb.catalog import CatalogMetadata
from tests.unit.test_baseunit import assert_num_validation_errors


def test_basic_cube_metadata_validation():
    """Test that pydantic correctly marks a model as invalid when the wrong datatype is passed."""
    invalid_catalog_metadata = CatalogMetadata(title=None)
    errors = invalid_catalog_metadata.pydantic_validation()
    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert "none is not an allowed value" in error.message
    assert "title" in error.message


if __name__ == "__main__":
    pytest.main()
