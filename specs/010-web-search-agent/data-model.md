# Data Model — Web Search Agent Summary

This project is a beginner-friendly console agent, so data structures stay minimal and live in memory during a single run.

## Structure: SearchSession (dict-like)
- **question** (string): trimmed user question captured from the prompt. Validation enforces at least five characters.
- **mode** (string): either `"user"` for manual input or `"smoke_test"` when the default Linux search question runs.
- **results** (list of SearchItem): populated with Tavily responses; list can be empty if the search fails.
- **summary** (string): concise explanation generated from the top findings; kept under ~150 words.
- **notes** (list of strings): optional warnings (e.g., limited sources or API errors) shown after the summary.

## Structure: SearchItem (dict-like)
- **title** (string): headline from the Tavily result.
- **snippet** (string): short descriptive text returned by the API.
- **source_url** (string): link displayed for transparency.

## Usage Notes
- Instances can be simple `dict` objects or lightweight `dataclasses` inside `agente_web/` (e.g., `types.py`).
- Data is not persisted; each `SearchSession` is created and printed within one execution of `main.py`.
- When the smoke test runs, reuse the same `SearchSession` structure so manual and automated flows follow identical logic.
