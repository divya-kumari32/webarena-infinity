import pytest

from infra import recovery


def test_classify_429():
    assert recovery.classify_error("HTTP 429 Too Many Requests") == "RATE_LIMIT"


def test_classify_5xx():
    assert recovery.classify_error("502 Bad Gateway") == "SERVER_ERROR"
    assert recovery.classify_error("InternalServerError 500") == "SERVER_ERROR"


def test_classify_connection():
    assert recovery.classify_error("Connection reset by peer") == "CONNECTION"
    assert recovery.classify_error("read timed out") == "CONNECTION"


def test_classify_unknown_defaults_to_server_error():
    assert recovery.classify_error("weird unparseable text") == "SERVER_ERROR"


def test_backoff_schedule_rate_limit_caps_at_120():
    waits = [recovery.backoff_seconds("RATE_LIMIT", a, jitter=False) for a in range(1, 9)]
    assert waits[0] == 5
    assert waits == sorted(waits)        # monotonic non-decreasing
    assert max(waits) <= 120             # capped


def test_max_attempts_per_class():
    assert recovery.MAX_ATTEMPTS["RATE_LIMIT"] == 8
    assert recovery.MAX_ATTEMPTS["SERVER_ERROR"] == 4
    assert recovery.MAX_ATTEMPTS["CONNECTION"] == 3


def test_jitter_within_bounds(monkeypatch):
    # full jitter => result in [0, computed]
    monkeypatch.setattr(recovery.random, "random", lambda: 1.0)
    hi = recovery.backoff_seconds("RATE_LIMIT", 2, jitter=True)
    monkeypatch.setattr(recovery.random, "random", lambda: 0.0)
    lo = recovery.backoff_seconds("RATE_LIMIT", 2, jitter=True)
    assert lo == 0
    assert hi == recovery.backoff_seconds("RATE_LIMIT", 2, jitter=False)


def test_deployment_list_defaults_to_single():
    assert recovery.deployments("eval", config={}) == [recovery.DEFAULT_EVAL_MODEL]


def test_deployment_list_uses_config():
    cfg = {"EVAL_DEPLOYMENTS": ["a", "b"]}
    assert recovery.deployments("eval", config=cfg) == ["a", "b"]
