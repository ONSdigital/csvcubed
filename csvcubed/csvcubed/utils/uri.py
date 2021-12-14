"""
URI
---

Functions to help when working with URIs.
"""
import re
from unidecode import unidecode
from urllib.parse import urlparse
import rdflib


_multiple_non_word_chars_regex = re.compile(r"[^\w]+")
_last_uri_part_regex = re.compile(".*/(.*?)$")


def uri_safe(label: str) -> str:
    """
    Convert a label into something that can be used in a URI path segment.

    The function formerly known as :func:`pathify`.
    """
    return re.sub(
        r"-$", "", re.sub(r"-+", "-", re.sub(r"[^\w/]", "-", unidecode(label).lower()))
    )


def csvw_column_name_safe(label: str) -> str:
    """
    Converts a generic string into a string which is safe as the :attr:`name` property in a CSV-W column.

    :return: A :obj:`str` based on :obj:`label` which is safe to use to :attr:`name` columns in a CSV-W metadata file.
    """
    return _multiple_non_word_chars_regex.sub("_", label).lower()


def get_last_uri_part(uri: str) -> str:
    """
    Gets the last segment of a URI's path.

    :return: The segment of the URI after the last `/`.
    """

    maybe_match = _last_uri_part_regex.search(uri)
    if maybe_match:
        return maybe_match.group(1)

    raise Exception("Could not match last URI part")


def looks_like_uri(maybe_uri: str) -> bool:
    """
    Tests whether a :class:`str` looks like a URI.

    :return: whether the :class:`str` looks like a URI or not.
    """
    parse_result = urlparse(maybe_uri)
    return parse_result.scheme != ""


def get_data_type_uri_from_str(data_type: str) -> str:
    """
    Is it a uri? Find out, and return one.
    """
    if looks_like_uri(data_type):
        # It's already a full URI
        return data_type
    else:
        return str(rdflib.XSD[data_type])


def ensure_looks_like_uri(value: str) -> None:
    """
    Ensure that :obj:`value` looks like a URI.

    :raises ValueError: when :obj:`value` does not look like a URI.
    """
    if not looks_like_uri(value):
        raise ValueError(f"'{value}' does not look like a URI.")
        

def ensure_values_in_lists_looks_like_uris(values: list[str]) -> None:
    """
    Ensure that the values in a list (:obj:`values`) look like URIs.

    :raises ValueError: when :obj:`value` does not look like a URI.
    """
    for value in values:
        if not looks_like_uri(value):
            raise ValueError(f"'{value}' does not look like a URI.")
