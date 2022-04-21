import pkg_resources

__version__ = pkg_resources.require("csvcubed")[0].version
"""
    __version__ is following pep-0396 guidance - https://peps.python.org/pep-0396/
    The underlying value is set in `pyproject.toml`.
"""

