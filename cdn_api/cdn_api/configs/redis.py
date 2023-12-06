from redis.asyncio import Redis


redis: None | Redis = None


async def get_redis_client() -> Redis:
    if redis is None:
        raise RuntimeError("Redis client has not been defined.")

    return redis
