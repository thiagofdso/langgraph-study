"""Helper utilities to orchestrate Tavily tool usage."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List
from uuid import uuid4


def build_search_tool_calls(question: str, tool_name: str, *, max_results: int) -> List[Dict[str, Any]]:
    """Construct ToolCall dictionaries compatible with ToolNode."""

    return [
        {
            "id": f"search-{uuid4()}",
            "name": tool_name,
            "type": "tool_call",
            "args": {
                "query": question,
                "max_results": max_results,
            },
        }
    ]


def parse_tool_payload(content: Any) -> List[Dict[str, Any]]:
    """Normalize ToolMessage content emitted by TavilySearch."""

    if isinstance(content, list):
        candidate: Any = content
    elif isinstance(content, dict):
        candidate = content
    elif isinstance(content, str):
        try:
            candidate = json.loads(content)
        except json.JSONDecodeError:
            return []
    else:
        return []

    if isinstance(candidate, dict):
        results = candidate.get("results") or candidate.get("data") or []
    else:
        results = candidate

    normalized: List[Dict[str, Any]] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "title": str(item.get("title") or item.get("name") or "Sem título"),
                "url": str(item.get("url") or ""),
                "content": str(
                    item.get("content")
                    or item.get("snippet")
                    or item.get("text")
                    or ""
                ),
            }
        )
    return normalized


def merge_warnings(existing: Iterable[str] | None, *new_warnings: str) -> List[str]:
    """Return a copy of warnings with additional messages appended."""

    warnings = list(existing or [])
    warnings.extend(note for note in new_warnings if note)
    return warnings

