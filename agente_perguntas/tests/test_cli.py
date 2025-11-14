from __future__ import annotations

from pathlib import Path

from agente_perguntas import cli


def test_run_single_question_writes_log(graph, logger, env_settings: Path, caplog) -> None:
    caplog.set_level("INFO", logger="agente_perguntas")
    question = "Como altero minha senha?"
    result = cli.run_single_question(graph, question, logger=logger, thread_id="cli-auto")
    assert result.status == "respondido automaticamente"
    log_file = env_settings / "agent.log"
    assert log_file.exists()
    assert any(question in record.message for record in caplog.records)
    assert any("respondido automaticamente" in record.message for record in caplog.records)


def test_run_single_question_handles_interrupt(monkeypatch, graph, logger) -> None:
    captured = {"called": False}

    def fake_handle_interrupt(payload):
        captured["called"] = True
        return "Resposta humana", "Notas QA"

    monkeypatch.setattr(cli, "_handle_interrupt", fake_handle_interrupt)
    question = "Preciso falar com atendente humano"
    result = cli.run_single_question(graph, question, logger=logger, thread_id="cli-hitl")
    assert captured["called"] is True
    assert result.status == "encaminhar para humano"
    assert result.answer == "Resposta humana"
    assert result.notes == "Notas QA"
