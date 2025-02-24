from slowapi import Limiter
from slowapi.util import get_remote_address

class RateLimiterService:
    def __init__(self):
        """Initialize the rate limiter"""
        self.limiter = Limiter(
            key_func=get_remote_address,
        )

    def limit(self, limit_string: str, key_func=None):
        """Decorator to apply rate limiting with a specified limit and custom key function."""
        return self.limiter.limit(limit_string, key_func=key_func)

