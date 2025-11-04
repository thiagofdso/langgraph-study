"""Backward-compatible entry point for agente_tool."""

from __future__ import annotations

import sys
from typing import List, Optional

from agente_tool.cli import main as cli_main


def main(argv: Optional[List[str]] = None) -> int:
    """Delegate execution to the CLI module."""

    return cli_main(argv)


if __name__ == "__main__":  # pragma: no cover - script execution
    raise SystemExit(main(sys.argv[1:]))
