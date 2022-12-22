import logging
from requests_cache import CachedSession

from csvcubed.utils.createlocalcopyresponse import AdapterToServeLocalFileWhenHTTPRequestFails

_logger = logging.getLogger(__name__)


session = CachedSession(cache_control=True, use_cache_dir=True)
session.mount("http://", AdapterToServeLocalFileWhenHTTPRequestFails())
session.mount("https://", AdapterToServeLocalFileWhenHTTPRequestFails())
