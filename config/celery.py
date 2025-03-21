"""Module for defining celery configurations."""

from functools import lru_cache

from celery import Celery


@lru_cache
def get_celery_app(
    broker_url: str,
    backend_url: str,
    worker_prefetch_multiplier: int,
    worker_concurrency: int,
    broker_pool_limit: int,
    worker_max_tasks_per_child: int,
    worker_max_memory_per_child: int,
) -> Celery:
    """Get the configured celery application."""
    celery_app = Celery(
        "rental_house",
        broker=broker_url,
        backend=backend_url,
        include=["app.account.otp.tasks.email"],
    )
    celery_app.conf.update(
        worker_prefetch_multiplier=worker_prefetch_multiplier,
        worker_concurrency=worker_concurrency,
        broker_pool_limit=broker_pool_limit,
        worker_max_tasks_per_child=worker_max_tasks_per_child,
        worker_max_memory_per_child=worker_max_memory_per_child,
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        result_expires=60 * 60,
        accept_content=["json"],
        task_serializer="json",
        result_serializer="json",
        broker_connection_retry=True,
        broker_connection_retry_on_startup=True,
        broker_connection_max_retries=10,
        worker_send_task_events=False,
        worker_hijack_root_logger=False,
        task_time_limit=60,
        task_soft_time_limit=45,
        task_default_max_retries=3,
        task_default_retry_delay=60,
    )
    return celery_app
