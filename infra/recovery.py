"""Error classification, backoff schedule, and deployment-fallback config.

Light, defensive retry policy (the target environment is ~5 jobs, no quota).
Used by pipeline.py's phase wrappers. Deployment fallback is config-driven and
dormant when only one deployment is configured per model.
"""
from __future__ import annotations

import random

DEFAULT_EVAL_MODEL = "deepseek-v32-az"
DEFAULT_GEN_MODEL = "litellm/aws/glm-5"

MAX_ATTEMPTS = {
    "RATE_LIMIT": 8,
    "SERVER_ERROR": 4,
    "CONNECTION": 3,
}

# base*2**(attempt-1), capped
_BACKOFF = {
    "RATE_LIMIT": {"base": 5, "cap": 120},
    "SERVER_ERROR": {"base": 5, "cap": 80},
    "CONNECTION": {"base": 3, "cap": 60},
}


def classify_error(text: str) -> str:
    """Map an error string to RATE_LIMIT | SERVER_ERROR | CONNECTION."""
    t = (text or "").lower()
    if "429" in t or "rate limit" in t or "too many requests" in t or "overloaded" in t:
        return "RATE_LIMIT"
    if any(k in t for k in ("connection", "timed out", "timeout", "reset", "broken pipe")):
        return "CONNECTION"
    if any(k in t for k in ("500", "502", "503", "504", "server error", "internalservererror")):
        return "SERVER_ERROR"
    return "SERVER_ERROR"  # safe default: moderate retry


def backoff_seconds(error_class: str, attempt: int, *, jitter: bool = True) -> int:
    """Exponential backoff (seconds) for a given error class and 1-based attempt.

    With jitter=True applies full jitter: a random value in [0, computed].
    """
    cfg = _BACKOFF.get(error_class, _BACKOFF["SERVER_ERROR"])
    raw = cfg["base"] * (2 ** (attempt - 1))
    capped = min(raw, cfg["cap"])
    if jitter:
        return int(capped * random.random())
    return capped


def deployments(kind: str, config: dict) -> list[str]:
    """Ordered deployment list for 'eval' or 'gen'. Defaults to a single model."""
    if kind == "eval":
        return list(config.get("EVAL_DEPLOYMENTS") or [DEFAULT_EVAL_MODEL])
    if kind == "gen":
        return list(config.get("GEN_DEPLOYMENTS") or [DEFAULT_GEN_MODEL])
    raise ValueError(f"unknown deployment kind: {kind}")
