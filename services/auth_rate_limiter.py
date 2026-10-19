from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class AuthRateLimiter:
    """Process-local sliding-window limiter for authentication actions."""

    def __init__(self):
        self._attempts = defaultdict(deque)
        self._lock = Lock()

    def allow(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        now = monotonic()
        cutoff = now - window_seconds

        with self._lock:
            attempts = self._attempts[key]

            while attempts and attempts[0] <= cutoff:
                attempts.popleft()

            if len(attempts) >= limit:
                return False

            attempts.append(now)
            return True

    def cleanup(self, max_keys: int = 10000) -> None:
        """Remove expired entries and cap retained keys."""
        now = monotonic()

        with self._lock:
            for key in list(self._attempts):
                attempts = self._attempts[key]

                while attempts and attempts[0] <= now - 3600:
                    attempts.popleft()

                if not attempts:
                    del self._attempts[key]

            while len(self._attempts) > max_keys:
                self._attempts.pop(next(iter(self._attempts)))


auth_rate_limiter = AuthRateLimiter()