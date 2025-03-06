import redis.asyncio as redis  # Вместо aioredis
from triada.config.settings import REDIS_HOST
import asyncio

redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

if __name__ == '__main__':
    print(asyncio.run(redis_client.ping()))