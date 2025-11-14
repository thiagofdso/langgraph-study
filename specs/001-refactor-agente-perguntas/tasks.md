---

description: "Task list for the Reestruturar Agente Perguntas feature"
---

# Tasks: Reestruturar Agente Perguntas

**Input**: Design documents from `/specs/001-refactor-agente-perguntas/` (plan.md, spec.md, data-model.md, research.md, quickstart.md, contracts/faq-agent.yaml)
**Prerequisites**: Python 3.12 repo venv activated, langgraph/langchain-core/google-generativeai dependencies installed, access to `agente_perguntas` package
**Note**: Tasks follow the `.specify` workflow and align with the modular structure defined in `plan.md` plus user priorities from `spec.md`.
**Tests**: FR-007/US3 require pytest coverage for similarity helpers, graph nodes, CLI/HITL behavior, and logging output.

**Organization**: Tasks grouped by user story so each increment is independently implementable and testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Task can run in parallel (different files, no blocking dependency)
- **[Story]**: User story label (US1, US2, US3). Setup/Foundational/Polish omit the label.
- Include explicit file paths in every description

## Path Conventions

- Core agent code lives in `agente_perguntas/` with modules (`cli.py`, `config.py`, `graph.py`, `state.py`) plus `utils/`, `docs/`, `tests/`
- Shared repository docs such as `README.md`, `PROJETOS.md`, `graph-nodes-patterns.md`, and `.gitignore` sit at repo root
- Feature documentation stays under `specs/001-refactor-agente-perguntas/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the modular package layout and repository plumbing required before refactoring.

- [X] T001 Create modular skeleton in `agente_perguntas/` (add __init__.py, __main__.py stub, cli.py, config.py, graph.py, state.py, utils/, docs/, tests/, logs/.gitkeep) mirroring the structure described in `langgraph-tasks.md`.
- [X] T002 Update `.gitignore` and `requirements.txt` so `agente_perguntas/logs/` (except .gitkeep) stays ignored and ensure structlog/langgraph/langchain/google-generativeai/pytest pins cover the refactor scope.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create shared building blocks (configuration, state, helpers) consumed by all user stories.

**⚠️ CRITICAL**: Complete this phase before any user story work.

- [X] T003 Implement `AppConfig` loader with ENV validation, temperature/confidence clamping, and log directory bootstrap in `agente_perguntas/config.py` (maps to AgentConfiguration entity).
- [X] T004 [P] Define `AgentState` / `InteractionState` TypedDict with `add_messages` reducer and HITL fields in `agente_perguntas/state.py`.
- [X] T005 [P] Port FAQ seeds, demo questions, and prompt builders from legacy prompt.py into `agente_perguntas/utils/prompts.py`, ensuring normalization rules from data-model.md.
- [X] T006 Implement cosine/heuristic similarity helpers plus ranking API with threshold awareness in `agente_perguntas/utils/similarity.py`.
- [X] T007 Wire `agente_perguntas/utils/__init__.py` to export prompts, similarity helpers, logging, and node factories for downstream imports.
- [X] T008 Create structured logging factory (using structlog/logging) that ensures `config.log_dir` exists and returns PT-BR loggers in `agente_perguntas/utils/logging.py`.

**Checkpoint**: Configuration/state/similarity/logging helpers available for graph & CLI layers.

---

## Phase 3: User Story 1 - Operador executa fluxo padronizado (Priority: P1) 🎯 MVP

**Goal**: Allow an operator to run `python -m agente_perguntas` (demo or pergunta única) and receive FAQ answers or HITL escalation with logs, satisfying FR-001 to FR-005.
**Independent Test**: Run `python -m agente_perguntas`, ask a FAQ-covered and a FAQ-missing question, confirm responses/logs mirror the scenarios listed in `spec.md`.

### Tests for User Story 1
_All automated coverage for this story is consolidated under Phase 5 (US3) so QA owns the pytest suite; manual validation follows the Independent Test above._

### Implementation for User Story 1

- [X] T009 [US1] Implement `evaluate_question` and HITL resume helpers in `agente_perguntas/utils/nodes.py`, handling empty question rejection, confidence comparison, and manual notes capture aligned with InteractionState.
- [X] T010 [US1] Build `build_graph()` in `agente_perguntas/graph.py` using `StateGraph`, attach the evaluate node, configure `InMemorySaver`, and expose a module-level `GRAPH` for reuse.
- [X] T011 [US1] Create argparse-driven CLI in `agente_perguntas/cli.py` covering demo (`/demo`) and single-question (`/questions`) flows described in `contracts/faq-agent.yaml`.
- [X] T012 [US1] Wire CLI execution to `AppConfig` + structured logging so each interaction logs status, confidence, and summary to `agente_perguntas/utils/logging.py` outputs and terminal.
- [X] T013 [US1] Provide `python -m agente_perguntas` support via `agente_perguntas/__main__.py` delegating to `cli.main()` with proper exit codes and error surfacing.

**Checkpoint**: Operator workflow delivers consistent answers/logs and remains fully CLI-driven.

---

## Phase 4: User Story 2 - Pessoa desenvolvedora configura o projeto (Priority: P2)

**Goal**: Deliver clear setup docs, environment templates, and log guidance so new developers can configure/run the agent without guesswork.
**Independent Test**: Follow the README/quickstart from a clean clone—copy `.env.example`, set variables, run the demo, and verify logs appear where documented.

### Tests for User Story 2
_No automated tests requested; success validated by executing the documented onboarding steps._

### Implementation for User Story 2

- [X] T014 [P] [US2] Publish `agente_perguntas/.env.example` listing `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_TEMPERATURE`, `AGENTE_PERGUNTAS_CONFIDENCE`, and `AGENTE_PERGUNTAS_LOG_DIR` with descriptive comments.
- [X] T015 [US2] Rewrite `README.md` sections for agente_perguntas covering venv activation, env setup, CLI usage (`python -m agente_perguntas`, `--pergunta`), and log locations.
- [X] T016 [US2] Author `agente_perguntas/docs/operations.md` detailing escalation workflow, troubleshooting for missing API key/provider outage, and log-review procedures per research.md.
- [X] T017 [P] [US2] Create `agente_perguntas/docs/quickstart.md` mirroring quickstart.md steps (demo mode, pergunta única, pytest) with copy-pastable commands and expected outputs.

**Checkpoint**: Any developer can onboard via docs/env template without tribal knowledge.

---

## Phase 5: User Story 3 - QA valida a refatoração com testes (Priority: P3)

**Goal**: Provide a dedicated pytest suite so QA can run `pytest agente_perguntas/tests -v` and verify CLI, graph, and similarity behavior described in US1 & US2.
**Independent Test**: Execute `pytest agente_perguntas/tests -v`; suite passes and covers CLI demo/pergunta flows, HITL branch, similarity ranking, and log file creation.

### Tests for User Story 3 (write-first)

- [X] T018 [P] [US3] Set up `agente_perguntas/tests/conftest.py` (plus `__init__.py`) with fixtures for `AppConfig`, in-memory graph, demo questions, and temp log directories to isolate runs.
- [X] T019 [P] [US3] Create `agente_perguntas/tests/test_similarity.py` covering normalization, ranking ties, and threshold clamping scenarios from data-model.md.
- [X] T020 [P] [US3] Implement `agente_perguntas/tests/test_graph.py` asserting evaluate node auto-responses, HITL fallback paths (mocking `interrupt`), and empty-question handling.
- [X] T021 [P] [US3] Implement `agente_perguntas/tests/test_cli.py` (using CliRunner/subprocess) to confirm demo & `--pergunta` flows write structured logs and statuses as per contracts/faq-agent.yaml.

### Implementation for User Story 3

- [X] T022 [US3] Document QA execution steps and expected pytest output summary inside `agente_perguntas/docs/operations.md#qa` and `README.md` so the team can reproduce SC-002.

**Checkpoint**: QA has automated coverage plus documented steps to validate regressions quickly.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Align shared docs, contracts, and validation artifacts after story delivery.

- [X] T023 Update `PROJETOS.md` and `graph-nodes-patterns.md` with the new agente_perguntas modules/nodes so future agents reuse the documented responsibilities.
- [X] T024 Execute the documented quickstart end-to-end and append the validation checklist/results to `agente_perguntas/docs/quickstart.md` (date + tester notes).
- [X] T025 Reconcile `specs/001-refactor-agente-perguntas/contracts/faq-agent.yaml` with the final CLI payload/response formats, noting any new fields or status text.

---

## Dependencies & Execution Order

1. **Setup → Foundational**: Phase 1 (T001-T002) must finish before config/state helpers in Phase 2 (T003-T008).
2. **Foundational → User Stories**: US1-US3 all depend on Phase 2 helpers; start user stories only after T008 completes.
3. **User Story Priority**: Execute in priority order (US1 ➜ US2 ➜ US3) to honor MVP focus, but US2 can start once CLI skeleton (T011-T013) stabilizes.
4. **Polish**: Phase 6 tasks (T023-T025) depend on all user stories so docs/contracts match the final implementation.

## Parallel Execution Examples

- **Phase 2**: After T003, run T004 and T005 in parallel while another contributor handles T006; T007 waits for helper exports, T008 waits for config.
- **US1**: Once T009 finishes, a teammate can start T011 (CLI parsing) while another wires graph compilation in T010; T012 can run after T011 even before __main__ (T013).
- **US2**: T014 (.env.example) and T017 (quickstart doc) can proceed concurrently while T015 updates README and T016 expands operations doc.
- **US3**: Tests T019-T021 are parallel-friendly once fixtures (T018) exist, enabling multiple QA engineers to split files.

## Implementation Strategy

1. **MVP First**: Deliver US1 end-to-end (CLI + graph + logging) immediately after foundational work so stakeholders can validate operator experience quickly.
2. **Documentation Wave**: Tackle US2 right after MVP to ensure onboarding materials stay accurate while the flow is fresh.
3. **Testing Wave**: Build the pytest suite (US3) once functionality/docs stabilize, enabling QA to lock the regression harness (SC-002).
4. **Continuous Validation**: After every phase, run the independent test described above to keep increments shippable.
5. **Finalize**: Complete polish tasks to propagate knowledge (PROJETOS.md, graph-nodes-patterns.md, contract sync) before closing the feature.
