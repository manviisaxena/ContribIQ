from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from backend.core.config import get_settings

settings = get_settings()
broker = ListQueueBroker(url=settings.VALKEY_URL).with_result_backend(
    RedisAsyncResultBackend(
        redis_url=settings.VALKEY_URL,
        result_ex_time=86400,
        prefix_str="task-result",
    )
)
