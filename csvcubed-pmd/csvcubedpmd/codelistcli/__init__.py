from pathlib import Path
from typing import Any
import click


from .datetimecodelistgen import generate_date_time_code_lists_for_csvw_metadata_file


@click.group("codelist")
def codelist_group():
    """
    Work with codelists.
    """
    pass


@codelist_group.command("generate-datetime")
@click.argument(
    "csvcube",
    type=click.Path(exists=True, path_type=Path),
    metavar="CSVW_QB_METADATA_PATH",
)
def _generate_datetime_code_list(csvcube: Path):
    """
    Generate a date-time CSV-W codelist from a csvcubed CSV-W Metadata file.
    """

    print(f"Generating date/time code list from {csvcube}")
    files_created = generate_date_time_code_lists_for_csvw_metadata_file(
        csvcube.absolute()
    )
    for file in files_created:
        print(f"Created '{file}'")
