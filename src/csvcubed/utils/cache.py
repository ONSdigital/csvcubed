from requests_cache import CachedSession


session = CachedSession(cache_control=True, use_cache_dir=True)
