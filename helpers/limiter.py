from slowapi import Limiter
from slowapi.util import get_remote_address
from config import REDIS_URL


class RateLimiterService:
    def __init__(self):
        """Initialize the rate limiter"""
        self.limiter = Limiter(
            key_func=get_remote_address,
            storage_uri=REDIS_URL,
            in_memory_fallback_enabled=False,
        )

    def limit(self, limit_string: str, key_func=None):
        """Decorator to apply rate limiting with a specified limit and custom key function."""
        return self.limiter.limit(limit_string, key_func=key_func)
