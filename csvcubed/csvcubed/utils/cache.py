from requests_cache import CachedSession

def session(url):
    session = CachedSession(cache_control=True)
    response = session.get(url)
    return response