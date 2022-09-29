"""
Version
---

Utility to return csvcubed version specific infomation.
"""
from csvcubed.__init__ import __version__


def get_csvcubed_version_uri():
    version_number = f"https://github.com/GSS-Cogs/csvcubed/releases/tag/v{__version__}"
    return version_number
