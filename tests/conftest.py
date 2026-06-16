"""Shared pytest fixtures for pipeline hardening tests."""
import socket
from pathlib import Path

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def free_port() -> int:
    """Return an OS-assigned free TCP port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture
def tmp_app_dir(tmp_path: Path) -> Path:
    """An empty app directory under a temp path."""
    d = tmp_path / "app"
    d.mkdir()
    return d
