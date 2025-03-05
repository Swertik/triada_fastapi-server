import redis.asyncio as redis  # Вместо aioredis
from triada.config.settings import REDIS_PASSWORD

redis_client = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True, password=REDIS_PASSWORD)
