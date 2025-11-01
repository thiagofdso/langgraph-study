from unittest.mock import patch

import importlib
import logging
import sys

import pytest


@patch("builtins.input", return_value="Quantos estados tem o Brasil?")
@patch("agente_simples.cli.app.invoke", return_value={"resposta": "Resposta do agente: O Brasil possui 26 estados."})
def test_cli_main_success(mock_invoke, mock_input, capsys):
    """CLI should ask for input, invoke the graph, and print the response."""
    from agente_simples import cli

    with patch("agente_simples.cli.preflight_config_check", return_value=[]):
        cli.main()

    captured = capsys.readouterr()
    assert "26 estados" in captured.out
    mock_input.assert_called_once()
    mock_invoke.assert_called_once()


@patch("builtins.input", return_value="   ")
def test_cli_main_handles_empty_question(mock_input, capsys):
    """CLI should short-circuit when the operator submits an empty question."""
    from agente_simples import cli

    with patch("agente_simples.cli.preflight_config_check", return_value=[]):
        cli.main()

    captured = capsys.readouterr()
    assert "Pergunta vazia" in captured.out
    mock_input.assert_called_once()


@patch("builtins.input")
@patch("agente_simples.cli.app.invoke")
def test_cli_main_stops_on_config_failure(mock_invoke, mock_input, capsys):
    """Configuration failures must prevent question prompt or LLM invocation."""
    from agente_simples import cli

    failure = {
        "name": "GEMINI_API_KEY",
        "result": "fail",
        "message": "Configure GEMINI_API_KEY no arquivo .env antes de continuar.",
    }
    with patch("agente_simples.cli.preflight_config_check", return_value=[failure]):
        cli.main()

    captured = capsys.readouterr()
    assert "Configure GEMINI_API_KEY" in captured.out
    mock_invoke.assert_not_called()
    mock_input.assert_not_called()


def test_cli_logs_run_history(tmp_path, monkeypatch):
    """Logging should persist question and status information in the chosen directory."""
    monkeypatch.setenv("AGENTE_SIMPLES_LOG_DIR", str(tmp_path))

    import agente_simples.utils.logging as logging_mod

    for logger_name in ["agente_simples", "agente_simples.cli"]:
        logging.getLogger(logger_name).handlers.clear()

    logging_mod = importlib.reload(logging_mod)
    sys.modules["agente_simples.utils.logging"] = logging_mod

    import agente_simples.cli as cli_mod
    cli_mod = importlib.reload(cli_mod)

    with patch("agente_simples.cli.preflight_config_check", return_value=[]), patch(
        "agente_simples.cli.app.invoke",
        return_value={
        "resposta": "Resposta do agente: Tudo certo.",
        "status": "completed",
        "duration_seconds": 1.2,
    },
), patch("builtins.input", return_value="Pergunta de teste"):
        cli_mod.main()

    log_file = tmp_path / "agent.log"
    assert log_file.exists()
    contents = log_file.read_text(encoding="utf-8")
    assert "Pergunta de teste" in contents
    assert "completed" in contents

    monkeypatch.delenv("AGENTE_SIMPLES_LOG_DIR", raising=False)
    logging_mod = importlib.reload(logging_mod)
    sys.modules["agente_simples.utils.logging"] = logging_mod
    importlib.reload(cli_mod)
