from requests_cache import CachedSession

def start_session(url):
    session = CachedSession(cache_control=True)
    session.remove_expired_responses()
    response = session.get(url)
    return response