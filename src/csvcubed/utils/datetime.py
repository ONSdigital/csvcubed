"""
Csvcubed DateTime Utils
-----------------------

Functions for handling date time within csvcubed.
"""
import datetime
from typing import Union

from dateutil import parser


def parse_iso_8601_date_time(
    date_or_date_time: str,
) -> Union[datetime.date, datetime.datetime]:
    """
    Parses ISO 8601 Date Time.
    """
    dt = parser.isoparse(date_or_date_time)
    if dt.time() == datetime.time.min:
        return dt.date()

    return dt
