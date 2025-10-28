# Tasks: Multi-Agent Orchestration for Report Generation

**Input**: Design documents from `/specs/008-multi-agent-orchestration-report/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Note**: This task list is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear task generation and alignment with project goals.

**Tests**: The user explicitly requested not to create unit or integration tests, and to use `main.py` for testing.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Project Initialization)

**Purpose**: Project initialization and basic structure

- [x] T001 Create the directory `multi_agentes_orquestracao`
- [x] T002 Create an empty `__init__.py` file in `multi_agentes_orquestracao/__init__.py`
- [x] T003 Copy the `.env` file from `agente_simples` to `multi_agentes_orquestracao/.env`
- [x] T004 Create `requirements.txt` with `langgraph`, `google-generativeai`, `python-dotenv`, `langchain-google-genai`, `langchain` in `multi_agentes_orquestracao/requirements.txt`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Initialize the LLM (`gemini-2.5-flash`) and load environment variables in `multi_agentes_orquestracao/main.py`
- [x] T006 Define the `State` TypedDict and `Section` class in `multi_agentes_orquestracao/main.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate Comprehensive Report (Priority: P1) 🎯 MVP

**Goal**: A user provides a theme, and the system generates a comprehensive report. An orchestrator agent plans the report and determines sections, worker agents generate text for their assigned sections in parallel, and the orchestrator/synthesizer consolidates these sections into a final report.

**Independent Test**: Run `python multi_agentes_orquestracao/main.py` and verify that a multi-section report is generated and presented for a given theme (e.g., "O que são agentes de ia?").

### Implementation for User Story 1

- [x] T007 [US1] Implement the `orchestrator` function to dynamically generate `sections` using an LLM based on the `topic` in `multi_agentes_orquestracao/main.py`.
- [x] T008 [P] [US1] Implement the `worker` function to generate content for a given `Section` using an LLM in `multi_agentes_orquestracao/main.py`.
- [x] T009 [US1] Implement the `synthesizer` function to combine `completed_sections` into `final_report` in `multi_agentes_orquestracao/main.py`.
- [x] T010 [US1] Define the `assign_workers` function to distribute sections to workers in parallel using `Send` API in `multi_agentes_orquestracao/main.py`.
- [x] T011 [US1] Build the Langgraph graph with `orchestrator`, `worker`, `synthesizer` nodes and conditional edges in `multi_agentes_orquestracao/main.py`.
- [x] T012 [US1] Compile and execute the Langgraph workflow with a default topic (e.g., "O que são agentes de ia?") in `multi_agentes_orquestracao/main.py`.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T013 Add necessary imports and basic error handling to `multi_agentes_orquestracao/main.py`.
- [x] T014 Ensure `multi_agentes_orquestracao/main.py` is executable and prints the final report.
- [x] T015 Run `quickstart.md` validation for `/root/code/langgraph/specs/008-multi-agent-orchestration-report/quickstart.md`..

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3)**: Depends on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- `orchestrator` must run first to generate sections.
- `worker` functions can run in parallel after sections are generated.
- `synthesizer` depends on all `worker` functions completing.
- Graph building depends on all functions.
- Execution depends on the graph being built.

### Parallel Opportunities

- Within Phase 3, multiple `worker` agents can execute in parallel (T008).

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task: "Implement the `worker` function to generate content for a given `Section` using an LLM in multi_agentes_orquestracao/main.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently by running `python multi_agentes_orquestracao/main.py`.
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
