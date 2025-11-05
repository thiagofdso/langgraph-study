"""Module entry point delegating to the CLI main function."""

from __future__ import annotations

from agente_imagem.cli import main


if __name__ == "__main__":  # pragma: no cover - CLI entry point wrapper
    main()
