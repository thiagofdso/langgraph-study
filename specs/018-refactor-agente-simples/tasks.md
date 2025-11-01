# Tasks: Refactor Simple Agent

**Input**: Design documents from `/specs/018-refactor-agente-simples/` (spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md, langgraph-tasks.md)  
**Prerequisites**: plan.md (tech stack), spec.md (user stories), research.md (decisions), data-model.md (entities), contracts/agent.yaml (integration surface), langgraph-tasks.md (implementation blueprint)

**Note**: Tasks are grouped by user story to preserve independent delivery and testing. Tests are included where quality safeguards are mandated in the specification.

**Format**: `[ID] [P?] [Story] Description`

- `[P]`: Task can run in parallel with others in the same phase.  
- `[Story]`: User story label (US1, US2, US3).  
- Descriptions include exact file paths.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare directory scaffolding and shared configuration assets.

- [x] T001 Create `agente_simples/utils/__init__.py` to scaffold the utils package per langgraph-tasks.md guidance.  
- [x] T002 [P] Create `agente_simples/tests/__init__.py` to initialize the pytest package structure.  
- [x] T003 [P] Add `agente_simples/docs/.gitkeep` to establish the operations documentation directory described in langgraph-tasks.md.  
- [x] T004 Update `langgraph.json` to register the `agente_simples/graph.py:create_app` entry point.  
- [x] T005 [P] Generate `agente_simples/.env.example` with `GEMINI_*`, `AGENT_TIMEOUT_SECONDS`, and locale keys from langgraph-tasks.md.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared modules required by every user story.

- [x] T006 Implement `GraphState` and `DialogueInput` validation schema in `agente_simples/state.py`.  
- [x] T007 Implement `AppConfig` factories and environment loading in `agente_simples/config.py`.  
- [x] T008 [P] Implement logger factory with stdout + file handlers in `agente_simples/utils/logging.py`.  
- [x] T009 [P] Create default `SYSTEM_PROMPT` constant in `agente_simples/utils/prompts.py`.

---

## Phase 3: User Story 1 – Confident Question Answering (Priority: P1) 🎯 MVP

**Goal**: Operator executes the CLI once and receives a timely answer in Portuguese.  
**Independent Test**: Run CLI with valid `.env`, ask a representative business question, and confirm response within 10 seconds without manual intervention.

### Tests (write first, expect failures)

- [x] T010 [P] [US1] Add happy-path node unit tests in `agente_simples/tests/test_nodes.py`.  
- [x] T011 [P] [US1] Add graph invocation integration test in `agente_simples/tests/test_graph.py`.  
- [x] T012 [P] [US1] Add CLI success test in `agente_simples/tests/test_cli.py`.

### Implementation

- [x] T013 [US1] Implement validate/invoke/format nodes in `agente_simples/utils/nodes.py` following langgraph-tasks.md blueprint.  
- [x] T014 [US1] Export node helpers via `agente_simples/utils/__init__.py`.  
- [x] T015 [US1] Assemble the StateGraph workflow in `agente_simples/graph.py`.  
- [x] T016 [US1] Build CLI orchestration and stdout UX in `agente_simples/cli.py`.  
- [x] T017 [US1] Update `agente_simples/main.py` to delegate to `cli.main()` and remove legacy flow.  
- [x] T018 [US1] Add `agente_simples/__main__.py` to support `python -m agente_simples`.

**Checkpoint**: CLI answers valid questions end-to-end using the new modular structure.

---

## Phase 4: User Story 2 – Fast Issue Resolution (Priority: P2)

**Goal**: Maintain stakeholders receive actionable diagnostics for misconfiguration or provider faults.  
**Independent Test**: Run CLI with missing or invalid `.env` values and simulate provider faults; ensure instructions guide recovery without stack traces.

### Tests (write first, expect failures)

- [x] T019 [P] [US2] Add missing credential test in `agente_simples/tests/test_cli.py`.  
- [x] T020 [P] [US2] Add provider failure test in `agente_simples/tests/test_graph.py`.

### Implementation

- [x] T021 [US2] Implement `preflight_config_check` helper in `agente_simples/config.py`.  
- [x] T022 [US2] Surface actionable validation errors in `agente_simples/cli.py`.  
- [x] T023 [US2] Handle provider exceptions with fallback messaging in `agente_simples/utils/nodes.py`.

**Checkpoint**: CLI halts gracefully with remediation steps for configuration or provider issues.

---

## Phase 5: User Story 3 – Maintainable Operations Playbook (Priority: P3)

**Goal**: Provide maintainers with documentation and logs to manage the agent confidently.  
**Independent Test**: Follow docs to set up environment, trigger runs (success + failure), and inspect persisted logs and guidance.

### Tests (write first, expect failures)

- [x] T024 [P] [US3] Add log capture test in `agente_simples/tests/test_cli.py`.

### Implementation

- [x] T025 [US3] Ensure run metadata is logged in `agente_simples/cli.py` using `utils.logging`.  
- [x] T026 [P] [US3] Author operations runbook in `agente_simples/docs/operations.md`.  
- [x] T027 [P] [US3] Update `agente_simples/README.md` with setup, troubleshooting, and logging instructions.

**Checkpoint**: New maintainers can follow docs, verify logs, and operate the agent without prior context.

---

## Final Phase: Polish & Cross-Cutting

- [x] T028 Run quickstart validation steps from `specs/018-refactor-agente-simples/quickstart.md` and record outcomes in `agente_simples/docs/operations.md`.  
- [x] T029 Update `PROJETOS.md` entry for `agente_simples` with refactor summary and technical approach.

---

## Dependencies & Execution Order

1. **Phase 1 → Phase 2 → User Stories → Polish** (strict).  
2. **User Stories**: US1 (P1) must complete before US2 or US3 validation; US2 and US3 can begin after foundational modules but should respect insights from US1.  
3. **Within stories**: Tests (T010/T011/T012 etc.) precede implementation tasks. Nodes (`T013`, `T023`) must be in place before CLI updates relying on them.

Dependency Graph:
- Setup → Foundational → US1 → {US2, US3} → Polish  
- US2 depends on US1 deliverables (graph + CLI) for validation hooks.  
- US3 depends on US1 logging hooks and US2 diagnostics to document real flows.

---

## Parallel Execution Opportunities

- **Phase 1**: T002, T003, T005 can proceed in parallel after T001 scaffolds base package.  
- **Phase 2**: T008 and T009 may execute concurrently once T006/T007 define shared structures.  
- **US1**: T010–T012 test tasks can run in parallel; T013/T015 may proceed concurrently once tests are in place.  
- **US2**: T019/T020 can be handled simultaneously, as can T021–T023 after US1 checkpoint.  
- **US3**: Documentation tasks T026/T027 run parallel while T025 integrates logging.

---

## Implementation Strategy

1. **MVP (User Story 1)**: Deliver modular CLI answering capability with tests passing.  
2. **Diagnostics (User Story 2)**: Layer in validation and error handling once baseline works.  
3. **Operations (User Story 3)**: Finalize logging, documentation, and maintainability assets.  
4. **Polish**: Validate quickstart, sync project catalog, and ensure docs reflect final behavior.

---
