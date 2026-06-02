from rq import Worker

from app.core.logging import configure_logging
from app.core.redis import get_analysis_queue, get_redis_connection
from app.core.settings import get_settings


def main() -> None:
    settings = get_settings()
    configure_logging(settings)
    redis_connection = get_redis_connection()
    queue = get_analysis_queue(redis_connection)
    Worker([queue], connection=redis_connection).work()


if __name__ == "__main__":
    main()
