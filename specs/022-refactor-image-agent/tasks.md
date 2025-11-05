# Tasks: Refactor agente_imagem Structure

**Input**: Design documents from `/specs/022-refactor-image-agent/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Note**: This task list is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear task generation and alignment with project goals.

**Tests**: Tests are explicitly requested for regression confidence (User Story 3). Follow the listed tasks to create deterministic pytest coverage using mocks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Capture current behavior for regression comparison and prepare fixtures referenced by multiple stories.

- [X] T001 Capture baseline success markdown into `agente_imagem/tests/fixtures/baseline_success.md`
- [X] T002 Capture missing-image error output into `agente_imagem/tests/fixtures/baseline_missing_image.log`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the modular file skeleton required by all user stories before migrating logic.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Create package scaffold files (`config.py`, `state.py`, `graph.py`, `cli.py`, `__main__.py`, `utils/__init__.py`, `utils/io.py`, `utils/nodes.py`, `utils/logging.py`) under `agente_imagem/`
- [X] T004 Add module-level docstring stubs outlining responsibilities in each new file under `agente_imagem/`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Standardized Project Layout (Priority: P1) 🎯 MVP

**Goal**: Reorganize `agente_imagem` to mirror `agente_simples`, migrating logic into dedicated modules while preserving runtime behavior.

**Independent Test**: Inspect the `agente_imagem/` tree to confirm dedicated modules exist (`config.py`, `state.py`, `utils/`, `graph.py`, `cli.py`, `tests/`), then run `python agente_imagem/main.py` with `folder_map.png` and verify the output matches `tests/fixtures/baseline_success.md`.

### Implementation for User Story 1

- [X] T005 [P] [US1] Implement `AppConfig` and `config.require_api_key()` in `agente_imagem/config.py`
- [X] T006 [P] [US1] Define `GraphState` TypedDict and status constants in `agente_imagem/state.py`
- [X] T007 [P] [US1] Move image helpers into `agente_imagem/utils/io.py` with `ImageLoadError` and `ensure_sample_image`
- [X] T008 [P] [US1] Port node functions into `agente_imagem/utils/nodes.py` adopting names (`validate_input_node`, `prepare_image_node`, `invoke_model_node`, `format_response_node`)
- [X] T009 [US1] Replace inline logging with `get_logger()` in `agente_imagem/utils/logging.py` and update imports across `agente_imagem/`
- [X] T010 [US1] Update `agente_imagem/README.md` to document the modular layout and preserved behavior

**Checkpoint**: User Story 1 delivers a modular project structure with legacy behavior intact

---

## Phase 4: User Story 2 - CLI Friendly Entry Point (Priority: P2)

**Goal**: Expose a LangGraph-compatible factory and CLI so operators can run `agente_imagem` via the same tooling as other agents.

**Independent Test**: Run `langgraph run agente-imagem --input '{"image_path": "folder_map.png"}'` and confirm it executes successfully without code edits.

### Implementation for User Story 2

- [X] T011 [P] [US2] Compile the workflow and expose `create_app()`/`app` in `agente_imagem/graph.py`
- [X] T012 [US2] Export `app` and `create_app` via `agente_imagem/__init__.py`
- [X] T013 [US2] Implement CLI entry point with argument parsing in `agente_imagem/cli.py`
- [X] T014 [US2] Simplify `agente_imagem/main.py` to delegate to `agente_imagem.cli.main`
- [X] T015 [US2] Append the `agente-imagem` mapping to `langgraph.json` without altering existing entries
- [X] T016 [US2] Extend quickstart instructions in `specs/022-refactor-image-agent/quickstart.md` with CLI and LangGraph usage

**Checkpoint**: User Story 2 ensures the agent is discoverable and runnable via standard LangGraph tooling

---

## Phase 5: User Story 3 - Regression Confidence (Priority: P3)

**Goal**: Provide automated tests guaranteeing success and failure paths stay aligned with the pre-refactor behavior.

**Independent Test**: Execute `pytest -k agente_imagem -q`; ensure success path validates markdown output against `baseline_success.md` and failure path asserts error status/logging.

### Tests for User Story 3

- [X] T017 [P] [US3] Mock Gemini happy-path test in `tests/test_agente_imagem.py` asserting markdown parity with `tests/fixtures/baseline_success.md`
- [X] T018 [P] [US3] Mock missing-image test in `tests/test_agente_imagem.py` verifying `status == "error"` and log message from `baseline_missing_image.log`
- [X] T019 [US3] Add helper fixture(s) in `tests/test_agente_imagem.py` for creating temporary images and resetting sample fallback

**Checkpoint**: Automated tests confirm refactor parity for primary and error flows

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Consolidate documentation, governance updates, and consistency checks across the refactored agent.

- [X] T020 Update `PROJETOS.md` with the refactor summary and technical approach for `agente_imagem`
- [X] T021 Append `prepare_image` node description to `graph-nodes-patterns.md`
- [X] T022 [P] Run command sequence from `specs/022-refactor-image-agent/quickstart.md` to validate end-to-end behavior

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 → Phase 2**: Baseline fixtures must exist before scaffolding to preserve regression targets.
- **Phase 2 → Phases 3–5**: Modular skeleton (files and docstrings) must be created before implementing story-specific logic.
- **Phase 3 (US1)** is prerequisite for **Phase 4 (US2)** and **Phase 5 (US3)** because CLI integration and tests rely on the modularized codebase.
- **Phase 6** depends on completion of all prior phases to ensure documentation reflects the final architecture.

### User Story Dependencies

1. **US1 (P1)** → unlocked after Phase 2.
2. **US2 (P2)** → depends on US1 completion since CLI factory wraps the reorganized modules.
3. **US3 (P3)** → depends on US1 (modules) and references fixtures captured in Phases 1–2.

### Parallel Opportunities

- Tasks marked **[P]** (T003, T005–T008, T011, T017–T018, T022) can be executed concurrently by different contributors once their prerequisites are satisfied.
- Within US1, T005–T008 may proceed in parallel because they operate on distinct modules (`config.py`, `state.py`, `utils/io.py`, `utils/nodes.py`).
- US3 test tasks T017 and T018 can run concurrently after US1 completes because they mock Gemini independently.

## Implementation Strategy

1. **MVP (US1)**: Deliver modular structure with migrated logic, verified by baseline fixtures. This ensures the agent remains functional after refactor.
2. **Increment 2 (US2)**: Layer on CLI and LangGraph integration for operational parity.
3. **Increment 3 (US3)**: Add deterministic regression tests to guard future refactors.
4. **Polish**: Update governance docs (`PROJETOS.md`, `graph-nodes-patterns.md`) and run the documented quickstart to certify deployment readiness.
