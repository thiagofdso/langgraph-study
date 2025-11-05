# Tasks: Refactor agente_banco_dados Structure

**Input**: Design documents from `/specs/023-refactor-db-agent/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Note**: This task list é parte do processo orientado por especificação, garantindo alinhamento entre requisitos, planejamento e execução.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Capturar baseline funcional e topologia atual antes das mudanças.

- [X] T001 Executar baseline do relatório atual via `python agente_banco_dados/main.py` e salvar saída em `specs/023-refactor-db-agent/baseline.md`
- [X] T002 Documentar layout vigente de `agente_banco_dados/` em `specs/023-refactor-db-agent/current-structure.md` para referência

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Criar fundamentos reutilizáveis (estado e nodes) que suportam todas as histórias.

- [X] T003 Estruturar pacote utilitário inicial criando `agente_banco_dados/utils/__init__.py` com exports planejados
- [X] T004 Implementar `ProductSummary`, `SellerSummary` e `ReportState` em `agente_banco_dados/state.py` conforme data-model.md
- [X] T005 Implementar nodes puros `load_sales_metrics` e `render_sales_report` em `agente_banco_dados/utils/nodes.py` reutilizando `reporting.py`

---

## Phase 3: User Story 1 - CLI workflow preserved (Priority: P1) 🎯 MVP

**Goal**: CLI continua inicializando o banco e exibindo o relatório original.
**Independent Test**: Rodar `python agente_banco_dados/main.py` e comparar saída com `specs/023-refactor-db-agent/baseline.md`.

### Implementation

- [X] T006 [US1] Criar `agente_banco_dados/graph.py` com `create_app()` e `app` consumindo os nodes fundacionais
- [X] T007 [US1] Implementar orquestrador em `agente_banco_dados/cli.py` chamando `initialize_database()` e `app.invoke({})`
- [X] T008 [US1] Atualizar `agente_banco_dados/main.py` para delegar integralmente ao novo `cli.main`
- [X] T009 [US1] Validar CLI pós-refatoração comparando saída de `agente_banco_dados/main.py` com `specs/023-refactor-db-agent/baseline.md` e registrar diferenças em `specs/023-refactor-db-agent/baseline-diff.md`

**Checkpoint**: CLI preserva funcionalidade e gera relatório idêntico ao baseline.

---

## Phase 4: User Story 2 - LangGraph CLI compatível (Priority: P2)

**Goal**: Disponibilizar `create_app()` para consumo direto e validar uso programático.
**Independent Test**: Importar `from agente_banco_dados import create_app` e verificar `create_app().invoke({})["report_markdown"]`.

### Implementation

- [X] T010 [US2] Expor `app` e `create_app` em `agente_banco_dados/__init__.py` mantendo importações limpas
- [X] T011 [US2] Adicionar teste programático em `tests/test_agente_banco_dados.py` garantindo `create_app().invoke({})` e conteúdo do relatório
- [X] T012 [US2] Documentar uso programático e via LangGraph CLI em `agente_banco_dados/README.md`

**Checkpoint**: `create_app()` está acessível publicamente, testado e documentado.

---

## Phase 5: User Story 3 - Projeto fácil de manter (Priority: P3)

**Goal**: Espelhar padrões de `agente_simples`, documentar responsabilidades e atualizar catálogos.
**Independent Test**: Revisão estrutural confirmando módulos especializados e documentação alinhada.

### Implementation

- [X] T013 [US3] Ampliar seções de arquitetura e responsabilidade de módulos em `agente_banco_dados/README.md`
- [X] T014 [US3] Garantir docstrings detalhadas em `agente_banco_dados/state.py`, `agente_banco_dados/utils/nodes.py` e `agente_banco_dados/graph.py`
- [X] T015 [US3] Atualizar `graph-nodes-patterns.md` com `load_sales_metrics` e `render_sales_report`
- [X] T016 [US3] Registrar o grafo em `langgraph.json` adicionando entrada incremental para `agente_banco_dados/graph.py:app`

**Checkpoint**: Estrutura modular documentada, catálogo de nodes atualizado e registro no LangGraph CLI completo.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Consolidar documentação, regressões e catálogo geral.

- [X] T017 Executar `pytest` focando em `tests/test_agente_banco_dados.py` e suíte existente para validar regressão
- [X] T018 Atualizar `PROJETOS.md` com o resumo técnico da refatoração do `agente_banco_dados`
- [X] T019 Consolidar instruções finais em `specs/023-refactor-db-agent/quickstart.md` alinhando passos de CLI e LangGraph

---

## Dependencies & Execution Order

1. **Phase 1 → Phase 2**: Capturar baseline antes de alterar qualquer módulo garante referência para comparações.
2. **Phase 2 → Phase 3**: Estado e nodes devem existir antes de compilar o grafo e reconstruir a CLI.
3. **Phase 3 → Phase 4**: Programmatic access depende do grafo estabilizado e validado pelo CLI.
4. **Phase 4 → Phase 5**: Documentação aprofundada e catalogação assumem que interfaces já estão expostas.
5. **Phase 5 → Phase 6**: Após todas as histórias, consolidar documentação, testes e catálogos globais.

### Story Completion Dependencies

- **US1 (P1)**: Depende apenas dos fundamentos (Phase 2).
- **US2 (P2)**: Depende da conclusão de US1 para reutilizar o grafo estabilizado.
- **US3 (P3)**: Depende de US1 e US2 para documentar estrutura final e atualizar catálogos.

---

## Parallel Execution Examples

- Durante **Phase 2**, T003 (estrutura do pacote) e T004 (estado) podem ser iniciados simultaneamente, mas T005 depende de ambos concluídos.
- Nas histórias, documentação complementar (T012, T013) pode ocorrer em paralelo com ajustes técnicos posteriores desde que os arquivos relevantes já existam.
- Em **Phase 6**, T017 (pytest) deve preceder T019 para refletir passos testados; T018 pode ser realizado em paralelo após histórias concluídas.

---

## Implementation Strategy

- **MVP**: Concluir US1 (Phase 3) garante que o CLI preserve funcionalidade — este é o marco mínimo para entrega.
- **Incremental Delivery**:
  1. Consolidar nodes e grafo (US1) preservando relatórios.
  2. Expor `create_app()` e validar uso programático (US2).
  3. Registrar padrões e atualizar documentação para manutenção (US3).
- Cada fase termina com um checkpoint verificável, permitindo revisões intermediárias e evitando regressões entre histórias.
