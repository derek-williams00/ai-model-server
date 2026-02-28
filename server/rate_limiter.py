"""In-memory rate limiter / quota tracker."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Optional

from server.config.models import RateLimitConfig


class QuotaExceeded(Exception):
    """Raised when a model's quota is exceeded."""


class RateLimiter:
    """Thread-safe tracker for per-model rate limits and daily token quotas."""

    def __init__(self) -> None:
        self._lock = Lock()
        # token usage per model per UTC day  {model: {date_str: tokens}}
        self._daily_tokens: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        # timestamps of recent requests for per-minute rate limiting
        self._request_times: dict[str, deque] = defaultdict(deque)

    def _today(self) -> str:
        return time.strftime("%Y-%m-%d", time.gmtime())

    def check_and_record(
        self,
        model_alias: str,
        limits: Optional[RateLimitConfig],
        tokens_used: int = 0,
    ) -> None:
        """Check limits before a request, then record usage.

        Raises :class:`QuotaExceeded` when a limit is breached.
        *tokens_used* should be the token count *after* the request returns;
        pass 0 when calling before the upstream request.
        """
        if limits is None:
            return
        with self._lock:
            now = time.monotonic()
            today = self._today()

            # --- requests per minute ---
            if limits.requests_per_minute is not None:
                dq = self._request_times[model_alias]
                # evict timestamps older than 60 s
                while dq and now - dq[0] > 60:
                    dq.popleft()
                if len(dq) >= limits.requests_per_minute:
                    raise QuotaExceeded(
                        f"Rate limit exceeded for '{model_alias}': "
                        f"{limits.requests_per_minute} req/min"
                    )
                dq.append(now)

            # --- daily token quota ---
            if limits.daily_token_limit is not None:
                used = self._daily_tokens[model_alias][today]
                if used + tokens_used > limits.daily_token_limit:
                    raise QuotaExceeded(
                        f"Daily token limit exceeded for '{model_alias}': "
                        f"{limits.daily_token_limit} tokens/day"
                    )
                self._daily_tokens[model_alias][today] += tokens_used

    def record_tokens(self, model_alias: str, tokens: int) -> None:
        """Add *tokens* to today's usage counter for *model_alias*."""
        with self._lock:
            self._daily_tokens[model_alias][self._today()] += tokens

    def daily_usage(self, model_alias: str) -> int:
        """Return today's cumulative token usage for *model_alias*."""
        with self._lock:
            return self._daily_tokens[model_alias][self._today()]
