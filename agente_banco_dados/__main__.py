"""Module entry point forwarding to the CLI main function."""

from __future__ import annotations

from agente_banco_dados.cli import main


if __name__ == "__main__":  # pragma: no cover - executed via `python -m`
    main()
