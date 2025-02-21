from slowapi import Limiter
from slowapi.util import get_remote_address

class RateLimiterService:
    def __init__(self):
        """Initialize the rate limiter"""
        self.limiter = Limiter(
            key_func=get_remote_address,
        )

    def limit(self, limit_string: str):
        """Decorator to apply rate limiting with a specified limit."""
        return self.limiter.limit(limit_string)
