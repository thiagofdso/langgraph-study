# Tasks: Relatório de Vendas com Insights Gemini

**Input**: Design documents from `/specs/001-gemini-sales-report/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Note**: This task list is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear task generation and alignment with project goals.

**Tests**: Included where they provide measurable verification of user stories; align with acceptance scenarios from the specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare environment guidance for Gemini usage.

- [X] T001 Create Gemini environment template in agente_banco_dados/.env.example documenting `GEMINI_API_KEY`, `GEMINI_MODEL` and `GEMINI_TEMPERATURE`.
- [X] T002 Update agente_banco_dados/README.md prerequisites with Gemini configuration steps and CLI execution instructions.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core structures shared by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Extend ReportState with InsightSummary and metadata fields in agente_banco_dados/state.py.
- [X] T004 Add SALES_INSIGHT_SYSTEM prompt and build_sales_prompt helper (with docstrings) in agente_banco_dados/utils/prompts.py.
- [X] T005 Implement generate_sales_insights helper using ChatGoogleGenerativeAI with latency capture in agente_banco_dados/utils/llm.py.
- [X] T006 Refactor agente_banco_dados/config.py to expose AppConfig dataclass, create_llm factory, and ConfigurationError messaging.
- [X] T007 Export prompts and LLM helpers through agente_banco_dados/utils/__init__.py to keep public API consistent.

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Receber diagnóstico guiado por IA (Priority: P1) 🎯 MVP

**Goal**: Gerar relatório narrativo com, no mínimo, três insights acionáveis baseados nos números da consulta ao SQLite.

**Independent Test**: Executar `python -m agente_banco_dados.cli` com LLM stubado e verificar que o Markdown contém a seção “## Insights gerados pela IA” com três blocos referenciando valores numéricos exibidos.

### Tests for User Story 1

- [X] T008 [US1] Create agente_banco_dados/tests/test_generate_insights.py with stubbed Gemini verifying três blocos de insights citando métricas.

### Implementation for User Story 1

- [X] T009 [US1] Implement generate_insights_node em agente_banco_dados/utils/nodes.py para acionar generate_sales_insights, guardar narrativa e latência.
- [X] T010 [US1] Update render_sales_report em agente_banco_dados/utils/nodes.py para anexar a seção “## Insights gerados pela IA” preservando tabelas existentes.
- [X] T011 [US1] Insert generate_insights node no fluxo em agente_banco_dados/graph.py entre load_sales_metrics e render_sales_report.

**Checkpoint**: User Story 1 funcional e testável de forma independente.

---

## Phase 4: User Story 2 - Conferir dados de origem (Priority: P2)

**Goal**: Garantir transparência sobre os dados usados, mantendo tabelas e registrando metadados (fonte e horário de geração).

**Independent Test**: Gerar relatório e confirmar presença das tabelas, nota da fonte, timestamp `generated_at` e metadados que permitam confrontar valores com o SQLite.

### Tests for User Story 2

- [X] T012 [US2] Add agente_banco_dados/tests/test_report_structure.py para validar tabelas, nota de fonte e timestamp `generated_at` no Markdown final.

### Implementation for User Story 2

- [X] T013 [US2] Enhance load_sales_metrics e render_sales_report em agente_banco_dados/utils/nodes.py para preencher `metadata.processed_records`, `metadata.generated_at` e manter a referência à fonte.
- [X] T014 [US2] Update agente_banco_dados/cli.py para exibir resumo de metadata (processed_records e generated_at) após o relatório, auxiliando conferência manual.

**Checkpoint**: User Stories 1 e 2 prontos e auditáveis de forma independente.

---

## Phase 5: User Story 3 - Entender limitações da IA (Priority: P3)

**Goal**: Fornecer mensagens claras e acionáveis quando a geração por IA falhar.

**Independent Test**: Executar o agente com `GEMINI_API_KEY` ausente e com LLM simulando exceção; em ambos os casos, verificar mensagem amigável, orientação de próximo passo e registro em `metadata.llm_error`.

### Tests for User Story 3

- [X] T015 [US3] Add agente_banco_dados/tests/test_generate_insights_errors.py cobrindo ausência de `GEMINI_API_KEY` e exceção simulada com mensagens orientativas.

### Implementation for User Story 3

- [X] T016 [US3] Implementar tratamento de erros em agente_banco_dados/utils/nodes.py para retornar fallback report_markdown e `metadata.llm_error` quando ocorrer ConfigurationError ou exceções do provider.

**Checkpoint**: Todas as user stories entregam valor e lidam com cenários críticos.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Governança e validação final.

- [X] T017 Atualizar graph-nodes-patterns.md documentando o node `generate_insights` e sua responsabilidade.
- [X] T018 Atualizar PROJETOS.md (seção agente_banco_dados) com o novo fluxo de insights e metadados.
- [X] T019 Validar quickstart executando `python -m agente_banco_dados.cli` e ajustando specs/001-gemini-sales-report/quickstart.md com resultados observados.

---

## Implementation Strategy

- Entregar o MVP cumprindo User Story 1 antes das demais, garantindo narrativa de insights funcional.
- Manter incremento incremental: adicionar transparência (US2) depois que a narrativa estiver estável e, em seguida, reforçar resiliência (US3).
- Aplicar TDD parcial nas histórias: escrever testes de verificação (T008, T012, T015) antes da implementação correspondente quando possível para guiar os requisitos.
- Guardar tempo no final para documentação institucional (graph-nodes-patterns.md, PROJETOS.md) e validação manual via quickstart.

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 → Phase 2**: Setup completa (T001–T002) antes da fundação.
- **Phase 2 → Phase 3–5**: T003–T007 habilitam todas as histórias; nenhuma história deve iniciar antes do término da fase fundacional.
- **Phase 3 → Phase 4 → Phase 5**: US1 (T008–T011) entrega MVP; US2 (T012–T014) depende da narrativa pronta; US3 (T015–T016) depende das estruturas anteriores para propagar mensagens.
- **Phase 6**: Executada após todas as histórias que forem implementadas.

### User Story Dependencies
- **US1**: Depende apenas da fase fundacional concluída.
- **US2**: Requer US1 para que a narrativa já esteja incorporada e possa ser auditada junto das tabelas.
- **US3**: Requer US1 e US2 para reutilizar a mesma estrutura e garantir mensagens consistentes sobre falhas de IA.

### Parallel Execution Examples
- **US1**: Após definir a interface de `generate_insights_node` (T009), o ajuste do grafo (T011) pode ocorrer em paralelo enquanto T010 finaliza a composição do relatório.
- **US2**: Com o formato de metadata decidido em T013, o teste de estrutura (T012) pode ser desenvolvido em paralelo ao ajuste do CLI (T014).
- **US3**: Os testes de falha (T015) podem ser escritos em paralelo ao tratamento de erros (T016), utilizando stubs para simular exceções.
- **Polish**: Atualizações de documentação (T017, T018) podem acontecer em paralelo à validação manual (T019) desde que o código esteja concluído.
