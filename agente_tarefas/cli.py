"""Deprecated CLI shim for agente_tarefas."""
from __future__ import annotations

from typing import Callable

LangGraphCommand = "venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0"
PromptFn = Callable[[str], str]
OutputFn = Callable[[str], None]

_DEPRECATION_MESSAGE = (
    "agente_tarefas não possui mais execução própria via `python -m` ou CLI legado.\n"
    "Inicie o agente exclusivamente pelo LangGraph CLI executando:\n"
    f"  {LangGraphCommand}\n"
    "Consulte `agente_tarefas/README.md` para detalhes."
)


def run_cli(*, input_fn: PromptFn | None = None, output_fn: OutputFn = print) -> None:
    """Inform callers that the CLI has been deprecated."""

    output_fn(_DEPRECATION_MESSAGE)
    raise SystemExit(1)


def main() -> None:  # pragma: no cover - shim
    run_cli()


if __name__ == "__main__":  # pragma: no cover
    main()
