"""
Version
---

Utility to return csvcubed version specific infomation.
"""
from importlib.metadata import version

__version__ = version("csvcubed")


def get_csvcubed_version_uri():
    version_number = f"https://github.com/GSS-Cogs/csvcubed/releases/tag/v{__version__}"
    return version_number
