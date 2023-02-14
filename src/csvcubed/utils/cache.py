from requests_cache import CachedSession

from csvcubed.utils.createlocalcopyresponse import (
    AdapterToServeLocalFileWhenHTTPRequestFails,
)

session = CachedSession(cache_control=True, use_cache_dir=True)
session.mount("http://", AdapterToServeLocalFileWhenHTTPRequestFails())
session.mount("https://", AdapterToServeLocalFileWhenHTTPRequestFails())
