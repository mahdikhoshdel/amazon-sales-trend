import redis
import pandas as pd


class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host="redis", port=6379, db=0, decode_responses=True
        )

    def is_cached(self, key):
        return self.redis_client.exists(key)

    def cache_data(self, key, df):
        self.redis_client.set(key, df.to_json())
        self.redis_client.expire(key, 3600)  # Cache for 1 hour

    def get_cached_data(self, key):
        data = self.redis_client.get(key)
        return pd.read_json(data)
