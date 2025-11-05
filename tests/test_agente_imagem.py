"""Regression tests for the refactored agente_imagem package."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from agente_imagem.config import config
from agente_imagem.graph import app
from agente_imagem.state import STATUS_ERROR, STATUS_FORMATTED

FIXTURES_DIR = Path("agente_imagem/tests/fixtures")


@pytest.fixture
def baseline_markdown() -> str:
    """Return the canonical markdown response used for regression checks."""

    return FIXTURES_DIR.joinpath("baseline_success.md").read_text().strip()


@pytest.fixture
def baseline_error_log() -> str:
    """Return the canonical log snippet for missing image scenarios."""

    return FIXTURES_DIR.joinpath("baseline_missing_image.log").read_text().strip()


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    """Create a temporary PNG image to exercise the happy path."""

    image_path = tmp_path / "sample.png"
    Image.new("RGB", (32, 32), color="red").save(image_path)
    return image_path


@patch.object(config, "create_llm")
def test_success_path(mock_create_llm: MagicMock, sample_image: Path, baseline_markdown: str) -> None:
    """The workflow should return markdown identical to the stored baseline."""

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = SimpleNamespace(content=baseline_markdown)
    mock_create_llm.return_value = mock_llm

    result = app.invoke({"image_path": str(sample_image)})

    assert result["markdown_output"].strip() == baseline_markdown
    assert result["status"] == STATUS_FORMATTED
    mock_create_llm.assert_called_once()


@patch.object(config, "create_llm")
def test_missing_image_logs_error(
    mock_create_llm: MagicMock,
    tmp_path: Path,
    baseline_error_log: str,
) -> None:
    """A missing image should short-circuit before invoking the LLM and log the baseline message."""

    missing_path = tmp_path / "does_not_exist.png"

    with patch("agente_imagem.utils.nodes.logger") as mock_logger:
        result = app.invoke({"image_path": str(missing_path)})

    assert result["status"] == STATUS_ERROR
    assert result["markdown_output"] is None
    mock_create_llm.assert_not_called()

    expected_prefix = baseline_error_log.splitlines()[0].split(":")[0]
    mock_logger.error.assert_any_call("Image file not found: %s", missing_path)
    assert any(expected_prefix in str(call.args[0]) for call in mock_logger.error.call_args_list)
