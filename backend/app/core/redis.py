from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from rq import Queue

from app.core.settings import get_settings


def get_redis_connection() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


def get_async_redis_connection() -> AsyncRedis:
    settings = get_settings()
    return AsyncRedis.from_url(settings.redis_url, decode_responses=True)


def get_analysis_queue(redis_connection: Redis | None = None) -> Queue:
    settings = get_settings()
    connection = redis_connection or get_redis_connection()
    return Queue(settings.analysis_queue_name, connection=connection)


def check_redis_health() -> bool:
    redis_connection = get_redis_connection()
    try:
        return bool(redis_connection.ping())
    finally:
        redis_connection.close()
