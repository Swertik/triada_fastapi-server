import redis.asyncio as redis  # Вместо aioredis

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
