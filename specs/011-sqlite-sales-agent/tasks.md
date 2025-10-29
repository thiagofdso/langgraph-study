# Tasks: SQLite Sales Agent

**Input**: Design documents from `/specs/011-sqlite-sales-agent/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Note**: This task list follows the specification-driven workflow. Tasks are grouped by user story so each slice can be implemented, demonstrated, and validated independently.

**Tests**: No automated tests were requested; focus is on manual verification via `python agente_banco_dados/main.py`.

**Organization**: Tasks adhere to the `[ID] [P?] [Story] Description` format with concrete file paths.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish project scaffold, environment configuration, and dependency baseline.

- [X] T001 Create base package file agente_banco_dados/__init__.py to initialize the new project module
- [X] T002 Copy environment template from agente_simples/.env to agente_banco_dados/.env
- [X] T003 Create local data directory agente_banco_dados/data/ and add placeholder file agente_banco_dados/data/README.md to keep it in version control
- [X] T004 Append SQLite artifact ignore pattern to .gitignore so agente_banco_dados/data/*.db stays untracked
- [X] T005 Ensure requirements.txt lists langgraph and langchain-core (add if missing) to support the new agent

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Provide shared configuration and entry-point scaffolding required by all user stories.

- [X] T006 Create agente_banco_dados/config.py with constants for database path, seed counts, and default model id
- [X] T007 Scaffold agente_banco_dados/main.py with a `main()` function, CLI guard, and placeholder calls for initialization and reporting

**Checkpoint**: With configuration and entry point in place, user story work can begin.

---

## Phase 3: User Story 1 – Seed local sales database (Priority: P1) 🎯 MVP

**Goal**: Automatically create and populate the SQLite database with sample products, sellers, and sales.

**Independent Test**: Delete agente_banco_dados/data/sales.db (if present), run `python agente_banco_dados/main.py`, and verify the database file, tables, and record counts are created without duplicates on subsequent runs.

### Implementation Tasks

- [X] T008 [US1] Define schema creation script and PRAGMA enforcement in agente_banco_dados/db_init.py
- [X] T009 [US1] Add seed datasets (≥5 products, ≥3 sellers, ≥20 sales) in agente_banco_dados/db_init.py using structured constants
- [X] T010 [US1] Implement initialize_database() in agente_banco_dados/db_init.py with transactions and INSERT OR IGNORE to keep seeding idempotent
- [X] T011 [US1] Invoke initialize_database() from agente_banco_dados/main.py and log table/row counts after seeding

**Checkpoint**: Database seeding runs deterministically and readies data for reporting.

---

## Phase 4: User Story 2 – Summarize sales insights locally (Priority: P2)

**Goal**: Query the seeded database and present top products and sellers in a markdown report (no external data access).

**Independent Test**: Run `python agente_banco_dados/main.py` after seeding and confirm the terminal shows markdown tables listing top three products by quantity and top three sellers by revenue, explicitly citing the local database as the source.

### Implementation Tasks

- [X] T012 [US2] Implement aggregate query helpers (top products & sellers) in agente_banco_dados/reporting.py using sqlite3
- [X] T013 [US2] Add markdown formatting helpers in agente_banco_dados/reporting.py to render the query outputs as tables
- [X] T014 [US2] Build LangGraph state graph in agente_banco_dados/main.py that orchestrates database queries and formatting without external tool calls
- [X] T015 [US2] Print the final markdown report in agente_banco_dados/main.py with a notice that insights come from the local database only

**Checkpoint**: Reporting flow delivers the required offline insights in markdown.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation and manual validation once both stories are complete.

- [X] T016 Update agente_banco_dados/README.md with setup steps, run command, and explanation of local-only data usage
- [X] T017 Run quickstart flow (`python agente_banco_dados/main.py`) and capture sample output snippet for README verification

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup → Foundational**: Complete Phase 1 before Phase 2.
- **Foundational → User Stories**: Phase 2 must finish before starting User Stories 1 or 2.
- **User Stories → Polish**: Finish targeted user stories prior to Phase 5.

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 2. No dependency on US2.
- **US2 (P2)**: Depends on Phase 2 and successful completion of US1 (needs seeded data).

### Task Dependencies (selected highlights)

- T002 depends on T001 (directory must exist before copying `.env`).
- T003 depends on T001 (data directory resides under new module).
- T010 depends on T008 and T009 (function uses schema & seed constants).
- T011 depends on T010 (main calls initializer after function exists).
- T014 depends on T012 and T013 (graph uses query + formatting helpers).

---

## Parallel Opportunities

- Within Phase 1, tasks T004 (.gitignore) and T005 (requirements.txt) can be done in parallel after T001–T003 finish because they touch different files.
- Once Phase 3 is stable, T012 (query helpers) can start while another contributor prepares markdown copy changes elsewhere (if needed), but edits within reporting.py itself should remain serialized.
- Phase 5 tasks T016 and T017 can be parallelized after both user stories are complete.

---

## Implementation Strategy

### MVP First (User Story 1)
1. Complete Phases 1 and 2.
2. Deliver Phase 3 (US1) to confirm deterministic database seeding.
3. Validate by running `python agente_banco_dados/main.py` and inspecting the database.

### Incremental Delivery
1. MVP (US1) establishes reliable local dataset.
2. Add US2 reporting capabilities to surface insights.
3. Finish with documentation polish once both stories function independently.

### Parallel Team Strategy
1. One contributor handles Phase 1–2 groundwork.
2. Another contributor starts US1 while a third prepares markdown/reporting logic (US2) once seeding stabilizes.
3. Reconvene for Phase 5 to finalize documentation and manual validation.
