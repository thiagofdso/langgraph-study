"""Logging helpers for the dynamic agent operations."""
from __future__ import annotations

from typing import List

from agente_tarefas.state import OperationError, OperationReport


def build_operation_log(report: OperationReport, error: OperationError) -> str:
    """Create a concise log string describing what happened in this turn."""

    segments: List[str] = []
    if error and error.get("code"):
        segments.append(f"error={error['code']}")
        if error.get("message"):
            segments.append(f"reason={error['message']}")
        return " | ".join(segments)

    additions = report.get("added") or []
    removals = report.get("removed") or []
    missing = report.get("missing") or []
    listing_only = report.get("listing_only")

    if listing_only:
        segments.append("action=list")
    if additions:
        segments.append(f"added={len(additions)}:{','.join(additions)}")
    if removals:
        segments.append(f"removed={len(removals)}:{','.join(removals)}")
    if missing:
        segments.append(f"missing={len(missing)}:{','.join(missing)}")
    if not segments:
        segments.append("action=none")
    return " | ".join(segments)


__all__ = ["build_operation_log"]
