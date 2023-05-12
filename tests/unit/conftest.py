import logging
import shutil
from pathlib import Path

import pytest
from platformdirs import PlatformDirs

from csvcubed.definitions import APP_ROOT_DIR_PATH
from csvcubed.utils.createlocalcopyresponse import map_url_to_file_path
from csvcubed.utils.log import start_logging

_user_log_dir = Path(PlatformDirs("csvcubed_testing", "csvcubed").user_log_dir)


@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    """Make sure to remove all the existing log files so we don't contaminate the tests."""
    if _user_log_dir.exists():
        shutil.rmtree(_user_log_dir)

    root_logger = logging.getLogger("csvcubed")
    for filter in root_logger.filters:
        root_logger.removeFilter(filter)
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    start_logging(log_dir_name="csvcubed_testing", selected_logging_level=logging.DEBUG)


@pytest.fixture()
def dummy_mapped_url():
    """
    This fixture is used to enable some tests to pass "bad input" URLs without causing an error
    due to a corresponding local file path not existing. It maps the URLs used in those tests to
    a file path that is known to exist. This allows connection errors and other such exceptions
    to happen in a testing scenario.
    """
    # Add test URL to dictionary when ready to use fixture
    test_dictionary = {
        # When a request is made with this URL in tests, the request will fail completely and not return any response as the domain does not exist.
        "//thisinputurlwillcauseanerror.com": APP_ROOT_DIR_PATH
        / "schema"
        / "cube-config"
        / "v1_3"
        / "schema.json",
        # When this URL is used in a test, a response will successfully be returned as purl.org exists, but the resource (/badinput) cannot be found.
        "//purl.org/csv-cubed/qube-config/badinput": APP_ROOT_DIR_PATH
        / "schema"
        / "cube-config"
        / "v1_3"
        / "schema.json",
        # When used in tests while online, this URL has the correct suffix to request template files and get a response, but this template doesn't exist/can't be found.
        "//raw.githubusercontent.com/GSS-Cogs/csvcubed/main/src/csvcubed/readers/cubeconfig/v1_0/templates/calendar-hourx.json": APP_ROOT_DIR_PATH
        / "readers"
        / "cubeconfig"
        / "v1_0"
        / "templates"
        / "calendar-year.json",
        # When used in tests while offline, this URL has the correct suffix to request template files and get a response, but this template doesn't exist/can't be found.
        "//purl.org/csv-cubed/qube-config/templates/calendar-hourx.json": APP_ROOT_DIR_PATH
        / "readers"
        / "cubeconfig"
        / "v1_0"
        / "templates"
        / "calendar-year.json",
    }
    map_url_to_file_path.update(test_dictionary)

    _logger = logging.getLogger(__name__)
    _logger.debug(map_url_to_file_path)
    yield None
    [map_url_to_file_path.pop(key) for key in list(test_dictionary.keys())]
    _logger.debug(map_url_to_file_path)
