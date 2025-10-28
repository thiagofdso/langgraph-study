# Tasks: Sequential Persona Generation Agent

**Input**: Design documents from `/specs/004-sequential-persona-agent/`
**Prerequisites**: plan.md, spec.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure: `multi_agentes_sequencial` directory
- [X] T002 Initialize Python virtual environment in `venv`
- [X] T003 Create `requirements.txt` with dependencies: `langgraph`, `google-generativeai`, `python-dotenv`, `pytest`, `langchain-google-genai`
- [X] T004 Copy `.env` from `agente_simples/.env` to `multi_agentes_sequencial/.env`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational tasks are required for this simple agent.

## Phase 3: User Story 1 - Generate and Format Persona (Priority: P1) 🎯 MVP

**Goal**: The system should generate a random persona and then format it into a JSON structure.

**Independent Test**: Trigger the persona generation process and verify that the final output is a valid JSON object containing a randomly generated persona with the specified attributes.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [US1] Create test file `tests/test_multi_agentes_sequencial.py`
- [X] T006 [US1] Write a failing test in `tests/test_multi_agentes_sequencial.py` that checks if the system generates a valid JSON persona.

### Implementation for User Story 1

- [X] T007 [US1] Implement the persona generation agent (Agent 1).
- [X] T008 [US1] Implement the JSON formatting agent (Agent 2).
- [X] T009 [US1] Orchestrate the sequential execution of Agent 1 and Agent 2 using `langgraph` in `multi_agentes_sequencial/main.py`.
- [X] T010 [US1] Make the tests in `tests/test_multi_agentes_sequencial.py` pass.

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T011 Create a `README.md` file for the `multi_agentes_sequencial` directory with instructions on how to run the system.

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
