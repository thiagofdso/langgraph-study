---

description: "Executable task list for Dynamic Task Agent Graph"

---

# Tasks: Dynamic Task Agent Graph

**Input**: Design documents from `/specs/001-task-agent-update/`
**Prerequisites**: plan.md (2025-11-19), spec.md (user stories P1–P3)

**Note**: Tasks follow the LangGraph Task Template v2.3 with phases aligned to setup, shared foundations, and individually testable user stories.

**Tests**: Required updates for `agente_tarefas/tests/test_nodes.py` and `agente_tarefas/tests/test_graph.py` per plan.

## Format: `[ID] [P?] [Story?] Description`

- **[P]** indicates tasks that can run in parallel.
- **[US#]** labels map to user stories from `spec.md`.
- Every description references exact file paths for clarity.

---

## Phase 1: Setup (Shared Infrastructure)

Purpose: Enforce LangGraph CLI as the only entrypoint and align docs/config.

- [X] T001 Update `agente_tarefas/cli.py`, `agente_tarefas/main.py`, and `agente_tarefas/__main__.py` to raise a helpful error directing users to `venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0`.
- [X] T002 Refresh LangGraph-only guidance in `agente_tarefas/README.md` and `PROJETOS.md` to describe the JSON operation contract and new workflow.
- [X] T003 Audit `langgraph.json` to ensure the `agente_tarefas` graph is exposed only via LangGraph CLI while preserving other graph registrations.

---

## Phase 2: Foundational (Blocking Prerequisites)

Purpose: Simplify shared state and create the reusable operation schema consumed by every story.

- [X] T004 Refactor `agente_tarefas/state.py` so `tasks` is a list of unique strings and `StateFactory` initializes the lean session fields described in the spec.
- [X] T005 [P] Create `agente_tarefas/utils/operations.py` defining the Operation schema plus validation helpers for `{"op":"listar"}`, `{"op":"add","tasks":[]}`, and `{"op":"del","tasks":[]}`.
- [X] T006 Normalize or remove obsolete round/timeline helpers in `agente_tarefas/utils/rounds.py` and `agente_tarefas/utils/timeline.py` so later nodes rely solely on the new schema.

**Checkpoint**: Once T004–T006 complete, user story work can run in parallel.

---

## Phase 3: User Story 1 – Atualizar lista em uma única mensagem (Priority: P1)

**Goal**: Convert a single LangGraph CLI message into ordered add/delete operations and reply with the updated list in the same turn.
**Independent Test**: With an empty list, invoke `venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0` and send “Adicione estudar e comprar mantimentos”; verify the transcript shows tasks added and the final list rendered immediately.

### Tests for User Story 1 (required)

- [X] T007 [P] [US1] Expand `agente_tarefas/tests/test_nodes.py` with fixtures covering parse/apply/summarize behaviors (multi-operation payload, duplicate filtering).
- [X] T008 [US1] Update `agente_tarefas/tests/test_graph.py` to assert the compiled graph runs `parse -> apply -> summarize` and produces deterministic task lists.

### Implementation for User Story 1

- [X] T009 [US1] Rewrite prompts in `agente_tarefas/utils/prompts.py` to demand strictly valid JSON operations and showcase listar/add/del examples from the spec.
- [X] T010 [US1] Implement `parse_operations` logic in `agente_tarefas/utils/nodes.py` (or adjacent module) to call the LLM, validate output via `operations.py`, and populate error context without mutating tasks.
- [X] T011 [US1] Implement `apply_operations` in `agente_tarefas/utils/nodes.py` to execute sequential add/delete operations with case-insensitive matching and skip-notes for missing tasks.
- [X] T012 [US1] Implement `summarize_response` in `agente_tarefas/utils/nodes.py` that builds the natural-language recap plus the resulting list per FR-008/FR-010.
- [X] T013 [US1] Rebuild `agente_tarefas/graph.py` to wire the new nodes inside `StateGraph` while preserving `AppConfig.create_checkpointer()` usage.

**Checkpoint**: After T009–T013, LangGraph CLI should support combined add/delete flows end-to-end.

---

## Phase 4: User Story 2 – Consultar lista atual sob demanda (Priority: P2)

**Goal**: Honor listar-only prompts without mutating tasks while confirming no changes occurred.
**Independent Test**: Preload tasks, send “Liste minhas tarefas” via LangGraph CLI, and confirm the response shows the ordered list plus “Nenhuma alteração realizada”.

- [X] T014 [P] [US2] Extend the parser in `agente_tarefas/utils/nodes.py` so a sole `{"op":"listar"}` instruction short-circuits mutation when no other operations exist.
- [X] T015 [US2] Adjust `summarize_response` formatting in `agente_tarefas/utils/nodes.py` to include a “no changes applied” banner for listar-only turns.
- [X] T016 [P] [US2] Add regression cases to `agente_tarefas/tests/test_nodes.py` proving listar requests leave the internal list untouched and still return the ordered tasks.

**Checkpoint**: Listing-only flows become independently shippable once T014–T016 pass.

---

## Phase 5: User Story 3 – Receber orientação quando a instrução for ambígua (Priority: P3)

**Goal**: Detect invalid or ambiguous instructions, respond with guidance, and guarantee zero unintended mutations.
**Independent Test**: Send “faça algo” through LangGraph CLI and verify the reply explains the `{op:...}` format, states no changes occurred, and the stored list remains identical.

- [X] T017 [P] [US3] Enhance validators in `agente_tarefas/utils/operations.py` to emit structured error codes/messages for malformed JSON, unsupported ops, or missing `tasks` arrays.
- [X] T018 [US3] Teach `parse_operations` in `agente_tarefas/utils/nodes.py` to branch into an error state that records guidance details without touching `state["tasks"]`.
- [X] T019 [US3] Update `summarize_response` in `agente_tarefas/utils/nodes.py` so ambiguity replies reiterate the required JSON format and confirm no changes were made.
- [X] T020 [P] [US3] Extend `agente_tarefas/tests/test_nodes.py` and `agente_tarefas/tests/test_graph.py` with negative cases proving zero mutations occur when errors are detected.

**Checkpoint**: Ambiguous inputs are safely handled once T017–T020 complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T021 [P] Update any retained logging/timeline helpers in `agente_tarefas/utils/timeline.py` (or `utils/__init__.py`) to capture operations executed, skipped deletions, and ambiguity guidance.
- [X] T022 Document the JSON operation contract and CLI-only usage in `agente_tarefas/docs/` (or extend `README.md`) so prompt authors understand supported flows.
- [X] T023 Record a QA handoff entry (e.g., `agente_tarefas/docs/manual-test.md`) requesting stakeholders to run ``venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0`` and validate add/list/delete/error scenarios.

---

## Dependencies & Execution Order

1. **Phase 1** → 2 → 3 → 4 → 5 → 6.
2. User Story phases can proceed in parallel only after Phase 2 finishes, but their delivery order should respect priorities (US1 → US2 → US3 for MVP sequencing).
3. Tests within each story should be authored before or alongside implementation (T007/T008 before T009–T013; T016 before T014–T015; T020 before T017–T019) to maintain coverage parity.

## Parallel Execution Examples

- **Phase 2**: T005 (operations schema) may run in parallel with T006 once T004 stabilizes.
- **US1**: T007 (node tests) and T009 (prompt rewrite) can proceed concurrently because they modify different files.
- **US2**: T014 (parser logic) and T015 (summaries) may run in parallel once T010–T013 land.
- **US3**: T017 (validators) and T020 (negative tests) can be executed simultaneously by different owners.
- **Polish**: T021 and T022 touch independent doc/log areas; T023 should wait until all other tasks pass.

## Implementation Strategy

- **MVP Scope**: Complete Phases 1–3 (Setup, Foundational, US1). This delivers dynamic add/delete flows with updated docs and allows manual CLI validation.
- **Incremental Delivery**:
  1. Ship MVP (US1) for feedback.
  2. Layer listar-only improvements (US2) for transparency.
  3. Finalize ambiguity guidance (US3) plus polish tasks for production readiness.
