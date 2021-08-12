"""
URI
---
"""
import re
from unidecode import unidecode
from urllib.parse import urlparse
import rdflib


multiple_non_word_chars_regex = re.compile(r"[^\w]+")
last_uri_part_regex = re.compile(".*/(.*?)$")


def uri_safe(label: str) -> str:
    """
    Convert a label into something that can be used in a URI path segment.

    The function formerly known as `pathify`.
    """
    return re.sub(
        r"-$", "", re.sub(r"-+", "-", re.sub(r"[^\w/]", "-", unidecode(label).lower()))
    )


def csvw_column_name_safe(label: str) -> str:
    return multiple_non_word_chars_regex.sub("_", label).lower()


def get_last_uri_part(uri: str) -> str:
    maybe_match = last_uri_part_regex.search(uri)
    if maybe_match:
        return maybe_match.group(1)

    raise Exception("Could not match last URI part")


def looks_like_uri(maybe_uri: str) -> bool:
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