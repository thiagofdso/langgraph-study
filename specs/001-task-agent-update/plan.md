# Implementation Plan: Dynamic Task Agent Graph

**Branch**: `001-task-agent-update` | **Date**: 2025-11-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-task-agent-update/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

We will retire the legacy `agente_tarefas` CLI/main entrypoints and operate the agent exclusively through the LangGraph CLI workflow defined in `langgraph.json`. The new graph will parse every user message into JSON operations (`listar`, `add`, `del`), mutate an in-memory list accordingly, and always conclude with the latest list plus a natural-language summary. The effort covers state simplification, new nodes (parse/apply/summarize), updated prompts, and refreshed tests for nodes/graph while keeping manual verification via `venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0` as the acceptance step.

## Technical Context

**Language/Version**: Python 3.12.3 (repo venv)  
**Primary Dependencies**: langgraph, langchain-core, google-generativeai (`gemini-2.5-flash` via project standard), python-dotenv  
**Storage**: In-memory session state (LangGraph MemorySaver checkpointer)  
**Testing**: pytest + bespoke LangGraph node/graph tests under `agente_tarefas/tests/`  
**Target Platform**: LangGraph CLI (`langgraph dev`) running locally/containerized (Linux)  
**Project Type**: Multi-agent monorepo with per-agent packages (`agente_*`)  
**Performance Goals**: Single-turn responses under ~3 seconds for listar requests; deterministic add/del sequencing per FR-003  
**Constraints**: No persistence beyond session, no task status tracking, operations limited to listar/add/del, JSON validation must prevent unintended mutations  
**Scale/Scope**: Single agent, single LangGraph CLI session at a time; state resets per session

## Constitution Check

- ✅ Documentation updates will add/adjust docstrings for any new helpers or nodes, satisfying Principle XXI.
- ✅ `langgraph.json` edits (if any) will append or toggle configuration without removing other agent registrations, upholding Principle XXII.
- ✅ New node responsibilities (parse/apply/summarize) will be cross-checked with `graph-nodes-patterns.md`; if they introduce novel patterns we will update that catalog, meeting Principle XXIII.

## Project Structure

### Documentation (this feature)

```text
specs/001-task-agent-update/
├── plan.md              # This file
├── spec.md              # Completed
├── langgraph-tasks.md   # Task list produced earlier
├── checklists/
│   └── requirements.md
└── (future) research.md, data-model.md, quickstart.md, contracts/
```

### Source Code (repository root)

```text
agente_tarefas/          # Target package (graph, state, CLI, utils, tests)
langgraph.json           # Declares graphs exposed to LangGraph CLI
PROJETOS.md              # Project index that must reference new workflow
venv/                    # Shared virtual environment
specs/                   # Specification-driven artifacts per feature
start-cli.sh             # Helper to boot LangGraph CLI locally
```

**Structure Decision**: Work is confined to `agente_tarefas/` (graph, state, utils, docs, tests), root-level `langgraph.json`, and documentation files (`agente_tarefas/README.md`, `PROJETOS.md`). No new top-level projects or agents are needed; we simply modernize the existing agent to the dynamic graph model described in the spec/tasks.

## Implementation Strategy

The plan follows the phases and tasks enumerated in `langgraph-tasks.md`, grouping them into actionable workstreams with explicit deliverables and verification steps.

### Phase 1 – Entry Enforcement & Docs Alignment (Tasks T001–T003)
1. Deprecate/guard `agente_tarefas/cli.py`, `main.py`, and `__main__.py` so they raise a helpful error directing users to `venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0`.
2. Update `agente_tarefas/README.md` plus the `PROJETOS.md` entry to describe the LangGraph-only workflow and highlight the JSON operation contract.
3. Review `langgraph.json` ensuring the agente_tarefas graph is registered only for LangGraph CLI usage (remove direct CLI hooks if lingering) while leaving other agent entries untouched.

### Phase 2 – Shared State & Operation Schema (Tasks T010–T012)
1. Simplify `agente_tarefas/state.py` so `tasks` is just a list of strings and remove unused metadata (ids/status/timeline remnants). Adjust `StateFactory` defaults accordingly.
2. Introduce `agente_tarefas/utils/operations.py` implementing the Operation schema (TypedDict/dataclass) plus validation helpers for `{"op":"listar"}`, `{"op":"add","tasks":[...]}`, `{"op":"del","tasks":[...]}` with deterministic ordering.
3. Delete or refactor utilities (`rounds.py`, `timeline.py`, prompt builders) that assumed three fixed rounds so subsequent phases can rely solely on the new schema.

### Phase 3 – US1 Dynamic Updates (Tasks T100–T114)
1. Redesign prompts in `agente_tarefas/utils/prompts.py` to instruct the LLM to emit strictly valid JSON operations; include examples from the spec (listar/add/del combos).
2. Add a `parse_operations` node that invokes the LLM, validates the returned JSON using the schema from Phase 2, and records user-friendly errors without mutating state.
3. Add an `apply_operations` node handling case-insensitive add/delete logic, ensuring duplicates are ignored and removal of missing tasks is reported but benign.
4. Add a `summarize_response` node that assembles the final message (summary + resulting list) per FR-008/FR-010.
5. Rebuild `agente_tarefas/graph.py` to wire the new nodes (`parse_operations -> apply_operations -> summarize_response`) with `StateGraph`, preserving the existing `AppConfig`/checkpointer hook.
6. Update tests: `agente_tarefas/tests/test_nodes.py` should cover parsing/validation/mutation paths (including multi-operation sequences), and `agente_tarefas/tests/test_graph.py` should assert that compiled graphs process state end-to-end using mocks/fakes as needed.

### Phase 4 – US2 Listar-Only Flow (Tasks T200–T202)
1. Extend the parser to allow `{op:"listar"}` as a stand-alone instruction even when the list is empty.
2. Ensure the summarization node formats listar-only responses distinctly (“Nenhuma alteração realizada…”) and skips mutation steps.
3. Add regression tests demonstrating listar requests leave the list untouched while still returning the ordered tasks.

### Phase 5 – US3 Ambiguity Guidance (Tasks T300–T303)
1. Enhance validation helpers to return structured error codes/messages for malformed JSON, unsupported operations, or missing `tasks` arrays.
2. Teach the parser node to branch into an error/clarification path that stores error details in state while preventing any task mutation.
3. Update the summarizer to produce guidance text describing the expected `{op:...}` format and confirm that the list is unchanged.
4. Expand node/graph tests with negative cases to prove no mutations occur when invalid instructions are supplied.

### Phase 6 – Polish & Cross-Cutting (Tasks T400–T402)
1. Review logging or timeline utilities (if retained) to record the outcome of each turn (tasks added/removed/listed, or errors explained).
2. Document the JSON contract in `agente_tarefas/docs/` (or README) for future prompt authors.
3. Upon completion, explicitly request stakeholder testing using ``venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0`` to validate live behavior; capture their sign-off.

## Testing & Validation

- **Automated**: Update and run `pytest agente_tarefas/tests/test_nodes.py agente_tarefas/tests/test_graph.py` to cover add/delete/listar flows and invalid-input handling.
- **Manual**: After code changes, run the LangGraph CLI manually (`venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0`) and simulate the user prompts described in the spec (add/remove combos, listar-only, ambiguous input) to ensure interactive fidelity.
- **Regression**: Confirm no other agents listed in `langgraph.json` regress by running existing smoke scripts or relying on CI (if available) for shared modules.

## Complexity Tracking

_(No constitution violations to record.)_
