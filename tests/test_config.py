from __future__ import annotations

from app.config import env_bool


def test_env_bool_defaults(monkeypatch):
    monkeypatch.delenv("EXAMPLE_BOOL", raising=False)
    assert env_bool("EXAMPLE_BOOL", True) is True
    assert env_bool("EXAMPLE_BOOL", False) is False


def test_env_bool_values(monkeypatch):
    monkeypatch.setenv("EXAMPLE_BOOL", "true")
    assert env_bool("EXAMPLE_BOOL", False) is True
    monkeypatch.setenv("EXAMPLE_BOOL", "0")
    assert env_bool("EXAMPLE_BOOL", True) is False

