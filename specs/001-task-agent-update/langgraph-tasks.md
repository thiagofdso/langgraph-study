---

description: "Implementation tasks for agente_tarefas dynamic LangGraph-only flow"

---

# Tasks: Dynamic Task Agent Graph

**Input**: Design documents from `/specs/001-task-agent-update/`
**Prerequisites**: plan.md (pending), spec.md (completed 2025-11-19)

**Note**: Task grouping mirrors the user stories so each slice can be implemented and verified independently while converging on the LangGraph-only experience.

**Tests**: Update coverage specifically in `agente_tarefas/tests/test_nodes.py` and `agente_tarefas/tests/test_graph.py`. Unit coverage elsewhere is optional unless referenced below.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Task can run in parallel (different files, no ordering risk)
- **[Story]**: Link to spec user story (US1, US2, US3)
- Always spell out relevant file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Remove deprecated entrypoints and enforce LangGraph CLI usage.

- [ ] T001 [P] [Shared] Update `agente_tarefas/cli.py`, `agente_tarefas/main.py`, and `agente_tarefas/__main__.py` to error out with a message pointing to `venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0`.
- [ ] T002 [Shared] Refresh `agente_tarefas/README.md` and top-level `PROJETOS.md` entry so they only describe the LangGraph CLI workflow and link to the new dynamic behavior.
- [ ] T003 [P] [Shared] Review `langgraph.json` and ensure the agente_tarefas app definition exposes only the LangGraph CLI entry (remove any CLI/main references if present).

---

## Phase 2: Foundational State & Operation Schema

**Purpose**: Prepare shared data structures that every user story depends on.

- [ ] T010 [Shared] Simplify `agente_tarefas/state.py` so `tasks` is a list of unique text strings (drop TaskItem status/id fields) and ensure `StateFactory` initializes the lean state described in the spec assumptions.
- [ ] T011 [P] [Shared] Introduce an `Operation` schema (either TypedDict or dataclass) plus validation helpers in `agente_tarefas/utils/operations.py` (new file) that support `{op:"listar"}`, `{op:"add","tasks":[]}`, `{op:"del","tasks":[]}` and preserve declared order.
- [ ] T012 [Shared] Update any utilities (e.g., `agente_tarefas/utils/rounds.py`, `timeline.py`) that referenced the old multi-round payload so they align with the new schema or are removed if obsolete.

**Checkpoint**: Once Phase 2 completes, the new graph nodes can consume the normalized state/operations.

---

## Phase 3: User Story 1 – Atualizar lista em uma única mensagem (Priority: P1)

**Goal**: Convert a single natural-language message into sequential add/delete operations and respond with the resulting list.
**Independent Test**: Simulate a LangGraph CLI turn with an empty list and verify that sending “Adicione estudar e comprar mantimentos” ends with a confirmation plus the list `["estudar","comprar mantimentos"]`.

### Tests (required for this story)

- [ ] T100 [P] [US1] Update `agente_tarefas/tests/test_nodes.py` to cover the new parsing + execution nodes, ensuring multiple operations in one payload mutate the state exactly once.
- [ ] T101 [US1] Refresh `agente_tarefas/tests/test_graph.py` so compiling the workflow produces the dynamic path and validates add/delete sequencing via a mock checkpointer.

### Implementation

- [ ] T110 [P] [US1] Replace the legacy round prompts with a single instruction in `agente_tarefas/utils/prompts.py` that forces the LLM to emit valid JSON operations (include examples mirroring the spec).
- [ ] T111 [US1] Create a `parse_operations` node in `agente_tarefas/utils/nodes.py` (or new module) that invokes the LLM with the current task list + user message, validates the JSON via the schema from T011, and surfaces friendly errors without mutating state.
- [ ] T112 [US1] Implement an `apply_operations` node that consumes the validated list, performs case-insensitive add/delete logic, and records which tasks were added, removed, or skipped (for reporting).
- [ ] T113 [US1] Add a `summarize_response` node that builds the final natural-language reply plus the updated list, ensuring every non-listar request still outputs the list after operations.
- [ ] T114 [US1] Rebuild `agente_tarefas/graph.py` to wire `parse_operations -> apply_operations -> summarize_response` with `StateGraph`, register the entrypoint, and keep the MemorySaver checkpointer hook intact.

**Checkpoint**: After this phase, LangGraph CLI can update the task list end-to-end for add/delete scenarios.

---

## Phase 4: User Story 2 – Consultar lista atual sob demanda (Priority: P2)

**Goal**: Support listar-only prompts that return the untouched ordered list.
**Independent Test**: Preload tasks, send “Liste minhas tarefas,” and assert the output mirrors the stored order with a statement that no changes occurred.

- [ ] T200 [P] [US2] Extend the parsing node to allow `{op:"listar"}` as a standalone instruction (even when the list is empty) and short-circuit execution paths accordingly.
- [ ] T201 [US2] Ensure the response node formats listar-only answers distinctly (e.g., “Nenhuma alteração realizada; tarefas atuais: ...”) per FR-007.
- [ ] T202 [US2] Add assertions in `agente_tarefas/tests/test_nodes.py` verifying listar does not mutate state and still emits the final list summary.

**Checkpoint**: Listing can be delivered independently and tested without add/delete logic.

---

## Phase 5: User Story 3 – Receber orientação quando a instrução for ambígua (Priority: P3)

**Goal**: Detect invalid or ambiguous inputs and prompt the user to restate their intent without altering tasks.
**Independent Test**: Send a nonsense message (“faça algo”) and verify the graph surfaces guidance plus the untouched list.

- [ ] T300 [P] [US3] Expand the validation helper to capture parsing errors (malformed JSON, unsupported ops, missing tasks array) and return structured error reasons.
- [ ] T301 [US3] Teach `parse_operations` to branch into an “explain” path when validation fails, storing an error code/details in state but skipping mutation.
- [ ] T302 [US3] Update the summarization node so ambiguous requests respond with instructions on providing `{op:...}` structures and explicitly confirm the list is unchanged.
- [ ] T303 [US3] Cover negative cases in `agente_tarefas/tests/test_nodes.py` and `test_graph.py`, ensuring no operations execute when errors occur.

**Checkpoint**: Users receive safe guidance and the list remains intact for invalid inputs.

---

## Phase 6: Polish & Cross-Cutting

- [ ] T400 [P] [Shared] Review logging/telemetry (if any) to ensure new nodes/timeline entries reflect add/del/listar outcomes and ambiguity explanations.
- [ ] T401 [Shared] Update `agente_tarefas/docs/` (or create a short doc) summarizing the JSON contract so future prompts stay aligned.
- [ ] T402 [Shared] Request manual verification from the stakeholder: **ask them to run** ``venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0`` and confirm add/list/delete flows plus error handling behave as described.

---

## Dependencies & Execution Order

- Phase 1 → Phase 2 → User Stories (Phases 3‑5) → Polish.
- User stories can run in parallel after Phase 2 if different engineers own distinct node files/tests.
- Tests tied to a story should be updated before implementation (per T100/T101/T202/T303) to keep regression coverage accurate.

