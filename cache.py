# cache.py
import time

CACHE = {}

def get_cache(key):
    if key in CACHE:
        data, ts, ttl = CACHE[key]
        if time.time() - ts < ttl:
            return data
        else:
            del CACHE[key]
    return None

def set_cache(key, data, ttl):
    CACHE[key] = (data, time.time(), ttl)
