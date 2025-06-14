from redis import Redis
import json

redis_client = Redis(host='localhost', port=6379, db=0)

def set_cache(key, value):
    redis_client.set(key, json.dumps(value))

def get_cache(key):
    value = redis_client.get(key)
    return json.loads(value) if value else None

def clear_cache(key):
    redis_client.delete(key)