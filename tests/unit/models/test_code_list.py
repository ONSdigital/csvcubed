import pandas as pd

from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.components.codelist import NewQbCodeList


def test_existing_cell_uri_template():
    df = pd.DataFrame({"Some Dimension": ["A", "B", "C"]})
    print(
        NewQbCodeList.from_data(
            metadata=CatalogMetadata("title"),
            data=df["Some Dimension"],
            csv_column_title="Some Dimension",
            cell_uri_template="http://reference.data.gov.uk/id/year/{+some_dimension}",
        )
    )
