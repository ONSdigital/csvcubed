import io
import pathlib
from typing import Any
import argparse


from .datetimecodelistgen import generate_date_time_code_lists_for_csvw_metadata_file


def configure_argument_parser(parser: argparse.ArgumentParser):
    parser.add_argument("--date-time",
                        help="Generate date-time code-list from a CSV-W.",
                        type=pathlib.Path)

    parser.set_defaults(func=_handle_args)


def _handle_args(args: Any):
    """
    Called upon parsing of CLI arguments. Will specify which params have been set.

    :param args:
    :return:
    """
    if "date_time" in args and args.date_time is not None:
        csvw_metadata: pathlib.Path = args.date_time
        print(f"Generating date/time code list from {csvw_metadata}")
        files_created = generate_date_time_code_lists_for_csvw_metadata_file(csvw_metadata.absolute())
        for file in files_created:
            print(f"Created '{file}'")
    else:
        print("codelist: Nothing to do")
