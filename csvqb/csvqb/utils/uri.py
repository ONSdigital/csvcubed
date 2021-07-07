import re
from unidecode import unidecode


multiple_non_word_chars_regex = re.compile(r"[^\w]+")
last_uri_part_regex = re.compile(".*/(.*?)$")


def uri_safe(label: str) -> str:
    """
      Convert a label into something that can be used in a URI path segment.

      The function formerly known as `pathify`.
    """
    return re.sub(r'-$', '',
                  re.sub(r'-+', '-',
                         re.sub(r'[^\w/]', '-', unidecode(label).lower())))


def csvw_column_name_safe(label: str) -> str:
    return multiple_non_word_chars_regex.sub("_", label).lower()


def get_last_uri_part(uri: str) -> str:
    maybe_match = last_uri_part_regex.search(uri)
    if maybe_match:
        return maybe_match.group(1)

    raise Exception("Could not match last URI part")