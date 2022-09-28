from ensurepip import version
import requests
import pytest

from csvcubed.utils.version import _get_csvcubed_version


def test_get_csvcubed_version():
    # The version number returned can have .dev0 appended which doesn't technically exist
    # as a valid release url.
    # So we check the prefix to this which should exist or if no .dev0 the whole URI is
    # checked.

    versionNumber = _get_csvcubed_version()

    if versionNumber[-10:] == "0.1.0.dev0":
        response = requests.get(versionNumber[:-5])
    else:
        response = requests.get(versionNumber)

    assert response.status_code == 200, f"{versionNumber} appears to not exist."
