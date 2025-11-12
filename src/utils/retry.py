"""Retry utilities with exponential backoff."""

import time
import logging
from typing import Callable, Type, Tuple
from functools import wraps

from .config import settings

logger = logging.getLogger(__name__)


def exponential_backoff_retry(
    max_retries: int = None,
    min_wait: int = None,
    max_wait: int = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator to retry function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default from settings)
        min_wait: Minimum wait time in seconds (default from settings)
        max_wait: Maximum wait time in seconds (default from settings)
        exceptions: Tuple of exception types to catch and retry

    Returns:
        Decorated function with retry logic
    """
    # Use settings defaults if not specified
    max_retries = max_retries or settings.MAX_RETRIES
    min_wait = min_wait or settings.RETRY_MIN_WAIT
    max_wait = max_wait or settings.RETRY_MAX_WAIT

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries - 1:
                        # Calculate wait time with exponential backoff
                        wait_time = min(min_wait * (2 ** attempt), max_wait)

                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {wait_time} seconds..."
                        )

                        time.sleep(wait_time)
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed for {func.__name__}: {str(e)}"
                        )

            # If all retries failed, raise the last exception
            raise last_exception

        return wrapper
    return decorator
