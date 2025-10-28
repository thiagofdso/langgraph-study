# Tasks: Calculator Agent

**Input**: Design documents from `/specs/003-calculator-agent/`
**Prerequisites**: plan.md, spec.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure: `agente_tool` directory
- [X] T002 Initialize Python virtual environment in `venv`
- [X] T003 Create `requirements.txt` with dependencies: `langgraph`, `google-generativeai`, `python-dotenv`, `pytest`, `langchain-google-genai`, `langchain`
- [X] T004 Copy `.env` from `agente_simples/.env` to `agente_tool/.env`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational tasks are required for this simple agent.

## Phase 3: User Story 1 - Agent Performs Calculation with Tool (Priority: P1) 🎯 MVP

**Goal**: The agent should perform a mathematical calculation using a dedicated calculator tool.

**Independent Test**: Provide a mathematical expression to the agent and verify that it correctly invokes the calculator tool and returns the accurate result.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [US1] Create test file `tests/test_agent_tool.py`
- [X] T006 [US1] Write a failing test in `tests/test_agent_tool.py` that checks if the agent correctly uses the calculator tool and responds with the accurate result for "300/4".

### Implementation for User Story 1

- [X] T007 [US1] Implement the calculator tool.
- [X] T008 [US1] Implement the agent logic in `agente_tool/main.py` using `langgraph` and `gemini-2.5-flash`, integrating the calculator tool.
- [X] T009 [US1] Make the tests in `tests/test_agent_tool.py` pass.

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T010 Create a `README.md` file for the `agente_tool` directory with instructions on how to run the agent.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Story 1 (Phase 3)**: Depends on Setup completion.

### Within Each User Story

- Tests MUST be written and FAIL before implementation.

## Implementation Strategy

### MVP First (User Story 1 Only)

1.  Complete Phase 1: Setup
2.  Complete Phase 3: User Story 1
3.  **STOP and VALIDATE**: Test User Story 1 independently
