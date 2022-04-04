import json
import logging
import requests

from json import JSONDecodeError
from pathlib import Path

from csvcubed.utils.cache import session

log = logging.getLogger(__name__)


def load_json_from_uri(uri: str) -> dict:
    """
    Loads a resource from a URI using the requests library
    Returns a dict of the response content or
    Raises the Exceptions once logging them
    """
    response = None
    try:
        response = session.get(uri)
        if not response.ok:
            # HTTP Get request failed - raise error
            msg = (
                f"Failed to retrieve the schema from: {uri}.Status-Code: {response.status_code}"
                f" - {response.text}"
            )
            log.error(msg)
            raise IOError(msg)
        return json.loads(response.text)

    except JSONDecodeError as err:
        log.error(f"JSON Decode Error: {repr(err)}")
        if response:
            log.error(f"The content being decoded: {response.text}")
        raise err

    except TypeError as err:
        log.error(f"JSON Type Error: {repr(err)}")
        raise err

    except Exception as err:
        log.error(
            f"The http get request to retrieve the schema returned the exception: {repr(err)}"
        )
        raise err


def read_json_from_file(file_path: Path) -> dict:
    """
    Reads the json content of the file located at file_path
    Returns the decoded json as a dict
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)

    except FileNotFoundError as err:
        log.error(f"File Not Found Error when looking for: {file_path}")
        raise err

    except JSONDecodeError as err:
        log.error(f"JSON Decode Error: {repr(err)}")
        raise err

    except TypeError as err:
        log.error(f"JSON Type Error: {repr(err)}")
        raise err

    except Exception as err:
        log.error(f"{type(err)} exception raised because: {repr(err)}")
        raise err
