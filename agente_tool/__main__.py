"""Module entry point for `python -m agente_tool`."""

from __future__ import annotations

from agente_tool.cli import main


if __name__ == "__main__":  # pragma: no cover - CLI bootstrap
    raise SystemExit(main())
