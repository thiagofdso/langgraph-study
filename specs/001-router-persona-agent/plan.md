# Implementation Plan: Router Persona Agent

**Branch**: `001-router-persona-agent` | **Date**: 2025-10-28 | **Spec**: /root/code/langgraph/specs/001-router-persona-agent/spec.md
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Develop a system with three agents: a router agent, an informal agent for young users (up to 30 years), and a formal agent for non-young users. The system will use Langgraph with global memory per `thread_id`, similar to `agente_memoria` and `multi_agentes_sequencial`. The program will simulate two conversations, one with a young user and one with a non-young user.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: langgraph, google-generativeai, python-dotenv, langchain-google-genai, langchain, langchain-core, langchain-community (Langgraph handles router agents via conditional edges and global memory via checkpointers like InMemorySaver, which is part of langgraph. No additional core dependencies are immediately required for these functionalities.)
**Storage**: In-memory state management for Langgraph
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: Single project (agent system)
**Performance Goals**: Responsive agent interactions
**Constraints**: Use `langgraph` for routing and global memory per `thread_id`. Leverage existing `agente_memoria` and `multi_agentes_sequencial` components. (The router agent will be implemented using conditional edges based on user age. Global memory per `thread_id` will be managed by configuring the Langgraph graph with an `InMemorySaver` checkpointer and passing a unique `thread_id` for each conversation.)
**Scale/Scope**: Two simulated conversations demonstrating persona-based routing.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No violations. This feature aligns with existing project patterns and does not introduce new architectural complexities that would conflict with the established constitution.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
multi_agentes_roteador/
├── __init__.py
├── main.py
├── router_agent.py
├── informal_agent.py
├── formal_agent.py
├── common.py
└── tests/
    └── test_router_persona_agent.py

**Structure Decision**: The selected structure is a single project within `multi_agentes_roteador`, containing separate modules for the router, informal, and formal agents, along with common utilities and tests.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
