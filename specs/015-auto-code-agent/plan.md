# Implementation Plan: Simplified Code Generation Loop

**Branch**: `015-auto-code-agent` | **Date**: October 31, 2025 | **Spec**: `specs/015-auto-code-agent/spec.md`
**Input**: Feature specification from `/specs/015-auto-code-agent/spec.md`

**Note**: This plan reflects the revised in-memory workflow requested on October 31, 2025.

## Summary

Implement a LangGraph-based agent in `agente_codigo/main.py` that follows the tutorial pattern (generation → execution → decision → reflection). The agent keeps all artifacts in memory, uses `gemini-2.5-flash` only for the generation and reflection nodes, enforces a five-iteration cap, and prints the final code to the console.

## Technical Context

**Language/Version**: Python 3.12.3  
**Primary Dependencies**: langgraph, langchain-core, langchain-google-genai, python-dotenv  
**Storage**: In-memory state only (no filesystem writes)  
**Testing**: Manual execution via CLI; optional lightweight pytest harness for state assertions  
**Target Platform**: Local CLI on Linux/macOS with network access for Gemini API  
**Project Type**: Single-script agent (console application)  
**Performance Goals**: Complete up to five iterations per run; each loop should finish within seconds given fast LLM responses  
**Constraints**: Do not create or modify files beyond existing `.env`; respect `MAX_ITERATIONS = 5`; reusable memory pattern similar to `agente_memoria`  
**Scale/Scope**: Single agent workflow focusing on iterative code improvement for one prompt

## Constitution Check

- Principle I: `agente_codigo/main.py` remains the executable entrypoint.  
- Principle IV: Default LLM is `gemini-2.5-flash`.  
- Principle V: LangGraph manages orchestration.  
- Principle VI: Keep structure minimal—single file with clear nodes.  
- Principle VIII: Python project within existing virtualenv; no new dependency management required.  
- Principle XIV: Plan, spec, tasks, and docs stay in sync with `.specify` framework.

No violations identified.

## Project Structure

### Documentation (this feature)

```text
specs/015-auto-code-agent/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
agente_codigo/             # Main implementation target (main.py, __init__.py, .env)
agente_memoria/            # Reference implementation for memory usage
specs/015-auto-code-agent/ # Feature documentation set
tests/                     # Repository-wide tests (add lightweight checks if needed)
```

**Structure Decision**: Modify only `agente_codigo/main.py` plus supporting docs under `specs/015-auto-code-agent/`. No new directories or modules required; reuse existing `.env` handling.

## Complexity Tracking

No exceptions to constitutional principles or additional governance approvals required.
