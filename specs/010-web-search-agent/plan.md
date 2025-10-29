# Implementation Plan: Web Search Agent Summary

**Branch**: `010-web-search-agent` | **Date**: October 29, 2025 | **Spec**: [specs/010-web-search-agent/spec.md](specs/010-web-search-agent/spec.md)
**Input**: Feature specification from `/specs/010-web-search-agent/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a LangGraph-driven agent in `agente_web` that accepts natural-language questions, searches the web via Tavily, gathers at least three relevant results, and returns a concise summary citing multiple sources. The primary entry point (`main.py`) will prompt the user (or automatically seed the smoke-test question) so no command-line arguments are required.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12.3 (repo virtualenv)  
**Primary Dependencies**: langgraph; langchain-core; google-generativeai; langchain-tavily  
**Storage**: N/A (ephemeral web search responses only)  
**Testing**: Manual execution via `python agente_web/main.py` (per instructions)  
**Target Platform**: Local CLI on Linux/macOS environments with internet access  
**Project Type**: Single CLI-oriented agent project under `agente_web`  
**Performance Goals**: Deliver smoke-test summary within 10 seconds and cite ≥2 sources for ≥80% of queries (per spec success criteria)  
**Constraints**: Must use gemini-2.5-flash model; use Tavily for web search; summary capped around 150 words; rely on `.env`-provided API keys  
**Scale/Scope**: Single-user interactive agent session processing one question at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Main File for Testing**: Plan includes runnable `agente_web/main.py` entry point → PASS
- **II. Continuous Learning & Best Practices**: Research captured LangGraph + Tavily integration guidance in `research.md` → PASS
- **III. Focused Testing Strategy**: Manual verification only; aligns with instruction to skip automated tests → PASS
- **IV. Standard LLM Model**: Will configure LangGraph to use `gemini-2.5-flash` via Google Generative AI → PASS
- **V. Standard Agent Framework**: LangGraph chosen as orchestration layer → PASS
- **VI. Code Simplicity**: Minimal modules (graph, tools, CLI) planned → PASS
- **VII. Documentation & Comments**: README and inline rationale will be provided → PASS
- **VIII. Python Development Standards**: Work within repo `venv` and manage deps via `requirements.txt` → PASS
- **IX. Change Approval Process**: No scope deviations planned; will consult user if expansion required → PASS
- **X. Project Module Structure**: `agente_web` will keep flat module layout, avoiding nested packages → PASS
- **XI. Relative Path Usage**: CLI will use relative imports within project → PASS
- **XII. Environment Configuration**: `.env` will be copied from `agente_simples` and adjusted for Tavily key → PASS
- **XIII. Preferred Research Tools**: Internet research (web.run) completed and cited in `research.md` → PASS
- **XIV. Specification-Driven Development**: Spec and plan in place before implementation → PASS

GATE STATUS: All constitution principles satisfied; ready for Phase 1 design.

## Project Structure

### Documentation (this feature)

```text
specs/010-web-search-agent/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
agente_web/
├── __init__.py
├── main.py            # CLI entry point for manual execution
├── graph.py           # LangGraph workflow definition
├── tools.py           # Tavily tool binding and helper utilities
├── summarizer.py      # Summary formatting and validation helpers
└── prompts.py         # System prompts / templates for summary generation

.env                   # Copied baseline from agente_simples for key configuration
requirements.txt       # Updated to include Tavily integration package if absent
```

**Structure Decision**: Extend repository root with new `agente_web` package mirroring other agents; keep supporting README in repo root while code lives inside `agente_web/`. No new test directories needed because verification occurs via CLI.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
