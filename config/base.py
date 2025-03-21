"""Module for defining base configurations."""

from .celery import get_celery_app
from .database import AsyncDatabaseConnection
from .logging import LoggingConfig
from .redis import AsyncRedisConnection
from .settings.base import Settings

# Settings
settings = Settings()

# Logging
logger = LoggingConfig(env=settings.env).get_logger()

# Database
db = AsyncDatabaseConnection(database_url=settings.database_url)

# Redis
redis_manager = AsyncRedisConnection(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    max_connection=settings.redis_pool_max_connection,
)

# Celery
celery_app = get_celery_app(
    broker_url=settings.celery_broker_url,
    backend_url=settings.celery_backend_url,
    worker_prefetch_multiplier=settings.celery_worker_prefetch_multiplier,
    worker_concurrency=settings.celery_worker_concurrency,
    broker_pool_limit=settings.celery_broker_pool_limit,
    worker_max_tasks_per_child=settings.celery_worker_max_tasks_per_child,
    worker_max_memory_per_child=settings.celery_worker_max_memory_per_child,
)
