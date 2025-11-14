"""Backward-compatible wrapper that proxies to ``agente_perguntas.cli``."""

from __future__ import annotations

from agente_perguntas.cli import main as cli_main


def main() -> int:
    """Delegate execution to the CLI module."""
    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
