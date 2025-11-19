"""Backward-compatible entry point that now only warns users."""
from agente_tarefas.cli import main

__all__ = ["main"]

if __name__ == "__main__":  # pragma: no cover
    main()
