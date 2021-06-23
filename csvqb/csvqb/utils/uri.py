import re
from unidecode import unidecode


def uri_safe(label: str) -> str:
    """
      Convert a label into something that can be used in a URI path segment.

      The function formerly known as `pathify`.
    """
    return re.sub(r'-$', '',
                  re.sub(r'-+', '-',
                         re.sub(r'[^\w/]', '-', unidecode(label).lower())))
