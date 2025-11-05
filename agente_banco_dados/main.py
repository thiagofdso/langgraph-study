"""Legacy entry point delegating to the CLI module."""

from __future__ import annotations

import sys
from pathlib import Path


if __package__ in {None, ""}:
    # Ensure the project root is on sys.path when executed as `python agente_banco_dados/main.py`.
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from agente_banco_dados.cli import main  # type: ignore
else:  # pragma: no cover - executed when using `python -m`
    from .cli import main  # type: ignore


if __name__ == "__main__":  # pragma: no cover - CLI convenience entry point
    main()
