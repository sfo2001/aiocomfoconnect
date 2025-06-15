"""
Decorators for aiocomfoconnect library.

This module contains reusable decorators for logging, timing, etc.
"""
import logging

_LOGGER = logging.getLogger(__name__)

def log_call(func):
    """Decorator to log method calls for command methods."""
    def wrapper(self, *args, **kwargs):
        _LOGGER.debug(f"{func.__name__} called")
        return func(self, *args, **kwargs)
    return wrapper
