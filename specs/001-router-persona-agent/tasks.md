# Tasks for Router Persona Agent

**Feature Branch**: `001-router-persona-agent`
**Implementation Plan**: `/root/code/langgraph/specs/001-router-persona-agent/plan.md`
**Feature Specification**: `/root/code/langgraph/specs/001-router-persona-agent/spec.md`

## Summary

This document outlines the tasks required to develop a system with a router agent and two persona agents (informal for young users, formal for non-young users) using Langgraph with global memory per `thread_id`. The system will simulate two conversations to demonstrate its functionality.

## Task Phases

### Phase 1: Setup

- [X] T001 Create the `multi_agentes_roteador` directory `/root/code/langgraph/multi_agentes_roteador`
- [X] T002 Create `__init__.py` in `multi_agentes_roteador/__init__.py`
- [X] T003 Create `common.py` in `multi_agentes_roteador/common.py`
- [X] T004 Create `router_agent.py` in `multi_agentes_roteador/router_agent.py`
- [X] T005 Create `informal_agent.py` in `multi_agentes_roteador/informal_agent.py`
- [X] T006 Create `formal_agent.py` in `multi_agentes_roteador/formal_agent.py`
- [X] T007 Create `tests` directory in `multi_agentes_roteador/tests`
- [X] T008 Create `test_router_persona_agent.py` in `multi_agentes_roteador/tests/test_router_persona_agent.py`

### Phase 2: Foundational Components

- [X] T009 Implement `get_llm` in `multi_agentes_roteador/common.py`
- [X] T010 Define `AgentState` and `create_graph_builder` in `multi_agentes_roteador/common.py` for shared graph setup
- [X] T011 Implement base agent logic (LLM invocation) in `multi_agentes_roteador/common.py`

### Phase 3: User Story 1 - Young User Interaction [US1]

- [X] T012 [US1] Implement informal agent logic in `multi_agentes_roteador/informal_agent.py`
- [X] T013 [US1] Create test for informal agent in `multi_agentes_roteador/tests/test_router_persona_agent.py`

### Phase 4: User Story 2 - Non-Young User Interaction [US2]

- [X] T014 [US2] Implement formal agent logic in `multi_agentes_roteador/formal_agent.py`
- [X] T015 [US2] Create test for formal agent in `multi_agentes_roteador/tests/test_router_persona_agent.py`

### Phase 5: User Story 3 - Simulated Conversations [US3]

- [X] T016 [US3] Implement router agent logic in `multi_agentes_roteador/router_agent.py`
- [X] T017 [US3] Implement main simulation logic in `multi_agentes_roteador/main.py`
- [X] T018 [US3] Create test for router agent and simulation in `multi_agentes_roteador/tests/test_router_persona_agent.py`

### Final Phase: Polish & Cross-Cutting Concerns

- [X] T019 Update `requirements.txt` with any new dependencies
- [X] T020 Update `GEMINI.md` with new technologies

## Dependencies

- Phase 1 tasks are sequential.
- Phase 2 tasks are sequential.
- Phase 3 depends on Phase 2.
- Phase 4 depends on Phase 2.
- Phase 5 depends on Phase 3 and Phase 4.
- Final Phase depends on all previous phases.

## Parallel Execution Opportunities

- Tasks within Phase 1 (creating files) can be executed in parallel.
- Tasks within Phase 3 (informal agent implementation and testing) can be executed in parallel.
- Tasks within Phase 4 (formal agent implementation and testing) can be executed in parallel.

## Independent Test Criteria

- **User Story 1**: The informal agent can be tested independently by providing an age <= 30 and a question, and verifying that the response contains emojis and informal language.
- **User Story 2**: The formal agent can be tested independently by providing an age > 30 and a question, and verifying that the response uses serious and cordial language.
- **User Story 3**: The program can be executed, and the output can be verified to show two distinct conversations, each demonstrating the appropriate agent persona based on the simulated age.

## Suggested MVP Scope

The MVP includes all tasks up to and including User Story 3, ensuring the full functionality of the router and persona agents with simulated conversations.

## Implementation Strategy

The implementation will follow a phased approach, starting with project setup, then foundational components, followed by the implementation and testing of each user story. The router agent will be implemented last, integrating the persona agents. Global memory will be handled using Langgraph's checkpointers.
