"""Legacy script entry point delegating to the CLI implementation."""

from __future__ import annotations

import sys
from pathlib import Path


if __package__ in (None, ""):
    # Allow execution via ``python agente_imagem/main.py`` by ensuring the repo root is on sys.path.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from agente_imagem.cli import main as cli_main  # type: ignore  # pylint: disable=wrong-import-position
else:
    from .cli import main as cli_main


def main() -> None:
    """Execute the CLI handler to maintain backwards compatibility."""

    cli_main()


if __name__ == "__main__":  # pragma: no cover - legacy script entry point
    main()
