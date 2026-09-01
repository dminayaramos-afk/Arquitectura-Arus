"""
ARUS
Rate Limiter
"""

from __future__ import annotations

from collections import deque
from time import time


class RateLimiter:

    def __init__(
        self,
        limit: int = 20,
        seconds: int = 60,
    ):

        self.limit = limit
        self.seconds = seconds
        self.calls = deque()

    def allowed(self):

        now = time()

        while self.calls and now - self.calls[0] > self.seconds:
            self.calls.popleft()

        if len(self.calls) >= self.limit:
            return False

        self.calls.append(now)

        return True
