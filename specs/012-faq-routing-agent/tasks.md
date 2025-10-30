# Tasks: FAQ Routing Agent

**Input**: Design documents from `/specs/012-faq-routing-agent/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Note**: Tasks grouped by user story to keep each slice independently deliverable.

**Tests**: No automated tests requested; manual verification via console output.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create baseline project files and environment scaffolding.

- [X] T001 Create package directory `agente_perguntas/` with `__init__.py`
- [X] T002 Copy `.env` template from `agente_simples/.env` to `agente_perguntas/.env`
- [X] T003 Add placeholder `agente_perguntas/README.md` describing project goal and manual run steps
- [X] T004 Ensure `requirements.txt` already lists langgraph/langchain-core/google-generativeai; append if missing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish prompt structure and main execution shell before story-specific work.

- [X] T005 Create `agente_perguntas/prompt.py` containing embedded FAQ markdown and helper to build system message
- [X] T006 Scaffold `agente_perguntas/main.py` with CLI entry point, LangGraph placeholders, and scripted three-question list

**Checkpoint**: Prompt builder and main skeleton exist; safe to implement story logic.

---

## Phase 3: User Story 1 – Answer known FAQ question (Priority: P1) 🎯 MVP

**Goal**: Match FAQ entries and answer automatically when confidence ≥ threshold.

**Independent Test**: Run `python agente_perguntas/main.py` and validate that the first scripted question (FAQ-covered) returns the stored answer with confidence ≥ threshold and status “respondido automaticamente”.

- [X] T007 [US1] Implement similarity heuristic in `agente_perguntas/prompt.py` or helper module to score FAQ entries
- [X] T008 [US1] Build LangGraph node in `agente_perguntas/main.py` that evaluates question, applies threshold, and records interaction as resolved when matched
- [X] T009 [US1] Log resolved interaction in-memory and print answer to console with confidence disclosure

**Checkpoint**: First question flows end-to-end using FAQ data.

---

## Phase 4: User Story 2 – Flag unresolved question (Priority: P2)

**Goal**: Detect low confidence and route to human with interrupt payload.

**Independent Test**: Running the same script, confirm the third scripted question (out of FAQ) triggers human escalation message including collected context.

- [X] T010 [US2] Extend LangGraph state to capture low-confidence branch and trigger `interrupt` payload with question metadata in `agente_perguntas/main.py`
- [X] T011 [US2] Format escalation notice for console output highlighting “Necessita atendimento humano”
- [X] T012 [US2] Append escalated interaction to summary tracking for final report

**Checkpoint**: Human routing behavior validated within scripted run.

---

## Phase 5: User Story 3 – Demonstrate scripted FAQ session (Priority: P3)

**Goal**: Produce a single-run demo covering two successes + one escalation and summary.

**Independent Test**: Execute `python agente_perguntas/main.py`; verify all three scripted questions run automatically and final summary lists resolved vs escalated items.

- [X] T013 [US3] Finalize scripted question list and loop execution order in `agente_perguntas/main.py`
- [X] T014 [US3] Generate readable final summary (resolved vs humano) printed after run
- [X] T015 [US3] Update `agente_perguntas/README.md` with documented human-in-loop test procedure referencing interrupt payload

**Checkpoint**: Demo run mirrors specification expectations.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation and validation touches.

- [X] T016 Review `quickstart.md` steps against actual behavior and adjust README if discrepancies found
- [X] T017 Manually execute `python agente_perguntas/main.py` to capture sample output for README (no files committed) and verify confidence thresholds

---

## Dependencies & Execution Order

- Setup (Phase 1) → Foundational (Phase 2) → US1 (P1) → US2 (P2) → US3 (P3) → Polish
- US2 depends on similarity/interaction scaffolding from US1.
- US3 depends on completed flows from US1 & US2.

---

## Parallel Opportunities

- Phase 1 tasks T001–T004 can run sequentially with potential parallelization between docs (T003) and requirements check (T004).
- During US2, T010 and T011 should run sequentially; T012 can follow once formatting is in place.
- Phase 6 tasks can be parallelized after all user stories are complete.

---

## Implementation Strategy

### MVP First
1. Finish Setup + Foundational.
2. Deliver US1 to ensure FAQ answering works (MVP).

### Incremental Delivery
1. Add US2 for human escalation logic.
2. Add US3 scripted flow + documentation.
3. Polish with final manual verification.

### Manual Testing Focus
- Emphasize running `python agente_perguntas/main.py` after each story completion to confirm behaviors before proceeding.
