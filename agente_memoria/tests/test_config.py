
"""Tests for the configuration of the memory agent."""
from __future__ import annotations

from unittest.mock import patch

from agente_memoria.config import preflight_config_check


@patch("agente_memoria.config.config.api_key", None)
def test_preflight_config_check_no_api_key():
    """Verify that the preflight check fails when the API key is missing."""
    results = preflight_config_check()
    assert any(r["result"] == "fail" for r in results)


@patch("agente_memoria.config.config.temperature", 2.0)
def test_preflight_config_check_invalid_temperature():
    """Verify that the preflight check warns about invalid temperature."""
    results = preflight_config_check()
    assert any(r["result"] == "warn" and "temperature" in r["name"].lower() for r in results)


@patch("agente_memoria.config.config.timeout_seconds", 2)
def test_preflight_config_check_low_timeout():
    """Verify that the preflight check warns about a low timeout."""
    results = preflight_config_check()
    assert any(r["result"] == "warn" and "timeout" in r["name"].lower() for r in results)
