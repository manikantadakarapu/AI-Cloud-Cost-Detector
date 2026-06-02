import logging
import time
from collections.abc import Callable
from typing import TypeVar

from azure.core.exceptions import AzureError, HttpResponseError, ServiceRequestError, ServiceResponseError

logger = logging.getLogger(__name__)
T = TypeVar("T")


RETRYABLE_EXCEPTIONS = (AzureError, HttpResponseError, ServiceRequestError, ServiceResponseError, TimeoutError)


def run_with_retries(operation_name: str, operation: Callable[[], T], *, max_retries: int = 3) -> T:
    attempt = 0
    while True:
        try:
            return operation()
        except RETRYABLE_EXCEPTIONS:
            attempt += 1
            if attempt >= max_retries:
                logger.exception(
                    "Retryable operation failed permanently",
                    extra={"extra": {"operation": operation_name, "attempt": attempt}},
                )
                raise
            delay_seconds = 2 ** (attempt - 1)
            logger.warning(
                "Retryable operation failed; retrying",
                extra={"extra": {"operation": operation_name, "attempt": attempt, "delay_seconds": delay_seconds}},
            )
            time.sleep(delay_seconds)
