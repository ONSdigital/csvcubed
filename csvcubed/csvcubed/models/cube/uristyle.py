"""
URI Style
---------

The style of URI to generate
"""

from enum import Enum


class URIStyle(Enum):
    """
    The URI style to use when outputting URLs
    """

    Standard = 0
    """The standard pattern (includes file name extensions)"""

    WithoutFileExtensions = 1
    """Without file name extensions"""
