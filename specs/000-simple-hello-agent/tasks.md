# Tasks: Simple Hello Agent

**Input**: Design documents from `/specs/001-simple-hello-agent/`
**Prerequisites**: plan.md, spec.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure: `agente_simples` directory
- [X] T002 Initialize Python virtual environment in `venv`
- [X] T003 Create `requirements.txt` with dependencies: `langgraph`, `google-generativeai`, `python-dotenv`, `pytest`
- [X] T004 Create `.env` file in `agente_simples` for `GEMINI_API_KEY`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational tasks are required for this simple agent.

## Phase 3: User Story 1 - Agent Responds to Question (Priority: P1) 🎯 MVP

**Goal**: The agent should answer the question "quantos estados tem o brasil?".

**Independent Test**: Run the agent and ask the question.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [US1] Create test file `tests/test_agent.py`
- [X] T006 [US1] Write a failing test in `tests/test_agent.py` that checks if the agent returns the correct answer.

### Implementation for User Story 1

- [X] T007 [US1] Implement the agent logic in `agente_simples/main.py` using `langgraph` and `gemini-2.5-flash`.
- [ ] T008 [US1] Make the test in `tests/test_agent.py` pass.

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T009 Create a `README.md` file for the `agente_simples` directory with instructions on how to run the agent.

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
