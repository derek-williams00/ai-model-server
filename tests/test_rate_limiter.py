"""Tests for the rate limiter."""
import time

import pytest

from server.config.models import RateLimitConfig
from server.rate_limiter import QuotaExceeded, RateLimiter


def test_no_limits_passes():
    limiter = RateLimiter()
    # Should not raise
    limiter.check_and_record("mymodel", None)


def test_daily_token_limit_exceeded():
    limiter = RateLimiter()
    limits = RateLimitConfig(daily_token_limit=100)
    limiter.record_tokens("m", 90)
    with pytest.raises(QuotaExceeded, match="Daily token limit"):
        limiter.check_and_record("m", limits, tokens_used=20)


def test_daily_token_limit_within_budget():
    limiter = RateLimiter()
    limits = RateLimitConfig(daily_token_limit=100)
    limiter.check_and_record("m", limits, tokens_used=50)
    assert limiter.daily_usage("m") == 50


def test_requests_per_minute_exceeded():
    limiter = RateLimiter()
    limits = RateLimitConfig(requests_per_minute=2)
    limiter.check_and_record("m", limits)
    limiter.check_and_record("m", limits)
    with pytest.raises(QuotaExceeded, match="Rate limit exceeded"):
        limiter.check_and_record("m", limits)
