from ensurepip import version
import requests
import pytest

from csvcubed.utils.version import get_csvcubed_version


def test_get_csvcubed_version():
    # The version number returned can have .dev0 appended which doesn't technically exist
    # as a valid release url.
    # So we check the prefix to this which should exist or if no .dev0 the whole URI is
    # checked.

    versionNumber = get_csvcubed_version()

    assert (
        "https://github.com/GSS-Cogs/csvcubed/releases/tag/v" in versionNumber
    ), f"{versionNumber} does not appear to be a release tag URL"
