"""Timeline helpers centralizing log mutations."""
from __future__ import annotations

from typing import List, Literal, Optional

from agente_tarefas.state import TimelineEntry

RoundId = Literal["round1", "round2", "round3"]


def append_entry(
    timeline: List[TimelineEntry],
    *,
    round_id: RoundId,
    user_input: str,
    agent_response: str,
    notes: Optional[str] = None,
) -> None:
    """Append a structured timeline entry."""

    entry: TimelineEntry = {
        "round_id": round_id,
        "user_input": user_input,
        "agent_response": agent_response,
    }
    if notes:
        entry["notes"] = notes
    timeline.append(entry)


__all__ = ["append_entry", "RoundId"]
