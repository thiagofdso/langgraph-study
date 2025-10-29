---
description: "Task list for implementing the Web Search Agent Summary feature"
---

# Tasks: Web Search Agent Summary

**Input**: Design documents from `/specs/010-web-search-agent/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Note**: Tasks are organized by user story to keep each increment independently implementable and testable.

**Tests**: No automated test tasks required (manual verification per quickstart).

**Organization**: Tasks grouped by phases → setup, foundational, user stories (by priority), polish.

## Format: `[ID] [P?] [Story] Description`

- **[P]** marks parallelizable tasks.
- **[Story]** indicates the user story label (US1, US2, US3) for story phases.
- Every description includes exact file paths.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare project structure, environment, and dependencies.

- [X] T001 Create project package and placeholder files in `agente_web/__init__.py` and `agente_web/main.py`.
- [X] T002 Copy baseline environment file from `agente_simples/.env` to repository root `.env`.
- [X] T003 Ensure `langchain-tavily` dependency is added in `requirements.txt`.
- [X] T004 Install dependencies inside the virtual environment with `pip install -r requirements.txt` (run from repo root).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core building blocks required by all user stories.

- [X] T005 Definir o estado mínimo do agente como dicionário dentro de `agente_web/main.py`.
- [X] T006 Carregar `.env` diretamente em `agente_web/main.py` e validar `GEMINI_API_KEY` e `TAVILY_API_KEY`.
- [X] T007 Declarar constantes de prompt no topo de `agente_web/main.py` para reaproveitamento.

**Checkpoint**: All shared scaffolding ready; user story work can begin.

---

## Phase 3: User Story 1 - Ask Question and Receive Summary (Priority: P1) 🎯 MVP

**Goal**: Let a user enter a natural-language question and receive a concise summary citing multiple sources.

**Independent Test**: Execute `python agente_web/main.py` e confirme que o resumo automático cita pelo menos duas fontes distintas.

### Implementation Tasks

- [X] T008 [US1] Consultar Tavily diretamente dentro do nó de busca em `agente_web/main.py`.
- [X] T009 [US1] Montar o fluxo LangGraph (buscar → resumir) definido inline em `agente_web/main.py`.
- [X] T010 [US1] Gerar o resumo com Gemini diretamente em `agente_web/main.py`, citando fontes.
- [X] T011 [US1] Configure single-run execution in `agente_web/main.py` to call the workflow and print the summary automatically.

**Checkpoint**: User can ask a question and receive a summarized answer referencing multiple sources.

---

## Phase 4: User Story 2 - Review Source Details (Priority: P2)

**Goal**: Exibir as fontes coletadas imediatamente para que o usuário possa inspecioná-las.

**Independent Test**: Após rodar `python agente_web/main.py`, verifique que a lista de fontes aparece no console com títulos e URLs ou, caso ausentes, surgem avisos.

### Implementation Tasks

- [X] T012 [US2] Formatar e exibir as fontes diretamente em `agente_web/main.py`.
- [X] T013 [US2] Ensure `agente_web/main.py` prints collected search results immediately after the summary.
- [X] T014 [US2] Keep warning notes in sync for missing or limited results within `agente_web/main.py`.

**Checkpoint**: Users can review result details or see warnings without rerunning the search.

---

## Phase 5: User Story 3 - Run Default Smoke Test (Priority: P3)

**Goal**: Provide a one-step smoke test that runs the predefined Linux search question and records the outcome for quick verification.

**Independent Test**: Rodar `python agente_web/main.py` e confirmar que o resumo é mostrado e o arquivo `agente_web/smoke_test_output.txt` é atualizado.

### Implementation Tasks

- [X] T015 [US3] Add a smoke-test flow in `agente_web/main.py` that triggers the default question without user input and reuses the graph pipeline.
- [X] T016 [US3] Persist the smoke-test `SearchSession` summary and sources to `agente_web/smoke_test_output.txt` for later review.

**Checkpoint**: Smoke test can be executed quickly and leaves an artifact for validation.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, manual validation, and cleanup.

- [X] T017 Update root `README.md` with setup, environment, and usage instructions referencing `agente_web/main.py`.
- [X] T018 Execute manual verification steps from `specs/010-web-search-agent/quickstart.md` and document results in `README.md` or project notes.

---

## Dependencies & Execution Order

1. **Phase 1 → Phase 2** → User story phases must wait for foundational setup.
2. **User Story Order**: US1 (MVP) → US2 (depends on results produced by US1) → US3 (reuses US1 flow).
3. **Polish**: Runs last after all user stories confirm acceptance checks.

## Parallel Execution Examples

- After Phase 2 completes, T008 (tools) and T010 (summarizer) can progress in parallel while coordinating interfaces defined in `SearchSession`.
- Within US2, T012 (resultado formatado em `main.py`) pode começar enquanto US1 finaliza, antecipando a visualização das fontes.
- During Polish, T017 (README) can proceed while T018 (manual verification) runs.

## Implementation Strategy

1. **MVP (US1)**: Deliver question-to-summary flow first, ensuring the LangGraph pipeline and console UX work end-to-end.
2. **Transparency (US2)**: Add result inspection and resiliency warnings once summaries are stable.
3. **Reliability (US3)**: Implement the automated smoke test and output recording to maintain quick regression checks.
4. **Documentation & Verification**: Final polish ensures learners can set up and validate the agent independently.

