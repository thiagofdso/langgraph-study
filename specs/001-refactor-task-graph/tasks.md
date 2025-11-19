# Tasks: Graph-Managed Task Workflow

**Input**: Design documents from `/specs/001-refactor-task-graph/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Note**: Tasks are grouped by user story to keep each slice independently deliverable and testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Capture the current behavior and align node naming before refactors begin.

- [x] T001 Document every place onde `tasks`, `completed_ids` e `timeline` são mutados no CLI em `agente_tarefas/cli.py` e `agente_tarefas/utils/rounds.py`, registrando o resumo em `specs/001-refactor-task-graph/research.md`.
- [x] T002 Review `graph-nodes-patterns.md` e planejar os nomes `prepare_tasks`, `complete_task`, `append_tasks` (ou equivalentes), anotando gaps caso seja preciso atualizar o catálogo após a implementação.
- [x] T003 Verificar se `specs/001-refactor-task-graph/contracts/graph-nodes.yaml` cobre todos os payloads planejados; listar ajustes necessários no mesmo diretório (`graph-nodes.yaml` comments ou CHANGELOG).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Preparar o estado compartilhado, scaffolding de nodes e fixtures de teste antes das histórias.

- [x] T004 Atualizar `agente_tarefas/state.py` com helpers/reducers mencionados no plano (ex.: `duplicate_notes`, fábrica de estado) garantindo docstrings claras.
- [x] T005 [P] Extrair/utilizar helpers reutilizáveis em `agente_tarefas/utils/nodes.py` para prompts/timeline, removendo dependência de mutações diretas do CLI.
- [x] T006 Configurar `agente_tarefas/graph.py` para aceitar múltiplos nodes (START → ... → END) e expor pontos de extensão, deixando comentários TODO onde cada node será ligado.
- [x] T007 Criar scaffolding de testes em `agente_tarefas/tests/test_nodes.py` (fixtures de `AgentState`, fakes de LLM/checkpointer) para suportar asserções nos próximos passos.

**Checkpoint**: Estado e scaffolding prontos; user stories podem iniciar.

---

## Phase 3: User Story 1 - CLI session managed by the graph (Priority: P1) 🎯 MVP

**Goal**: O CLI deve apenas coletar inputs; todos os updates de estado precisam ocorrer dentro dos nodes do grafo.
**Independent Test**: Executar `python -m agente_tarefas` com entradas determinísticas e verificar que `tasks`, `completed_ids` e `timeline` retornados pelo grafo refletem os inputs, sem mutações locais no CLI.

### Implementation & Tests

- [x] T008 [P] [US1] Implementar node `prepare_round1` em `agente_tarefas/utils/nodes.py` que popula `tasks` e timeline a partir das mensagens/payloads da Rodada 1.
- [x] T009 [P] [US1] Implementar node `complete_task` em `agente_tarefas/utils/nodes.py`, reutilizando `select_completed_task` e atualizando `tasks`/`completed_ids`/timeline.
- [x] T010 [P] [US1] Implementar node `append_tasks` (e sub-node de resumo se necessário) em `agente_tarefas/utils/nodes.py`, tratando duplicatas e notas conforme `collect_new_tasks`.
- [x] T011 [US1] Atualizar `agente_tarefas/graph.py` para encadear `prepare_round1 -> complete_task -> append_tasks`, configurando checkpointer e retornando estado completo.
- [x] T012 [US1] Refatorar `agente_tarefas/cli.py` para enviar apenas payloads/mensagens ao grafo, consumindo o estado retornado para impressão (sem mutar `tasks` locais).
- [x] T013 [P] [US1] Criar testes unitários dos nodes em `agente_tarefas/tests/test_nodes.py` garantindo que cada node atualiza `tasks`, `completed_ids` e `timeline` corretamente.
- [x] T014 [US1] Atualizar `agente_tarefas/tests/test_cli.py` para afirmar que o CLI reflete exatamente o estado vindo do grafo (sem copiar/mutar listas internas).

**Checkpoint**: CLI opera sobre o grafo; sessão completa funciona usando apenas nodes e passa nos testes dedicados.

---

## Phase 4: User Story 2 - Automated validation protects the flow (Priority: P2)

**Goal**: Reforçar a cobertura automática (pytest + main smoke) para detectar regressões sempre que o grafo alterar o estado.
**Independent Test**: Rodar `pytest agente_tarefas/tests -q` e `python -m agente_tarefas --ci` (ou fluxo equivalente) comprovando que estados retornados pelo grafo correspondem aos inputs e que falhas seriam detectadas.

### Implementation & Tests

- [ ] T015 [P] [US2] Adicionar fixtures determinísticas em `agente_tarefas/tests/conftest.py` (ou módulo equivalente) para mockar o LLM/checkpointer e permitir asserts de estado.
- [ ] T016 [US2] Expandir `agente_tarefas/tests/test_graph.py` com um cenário de rodada completa (round1→round3) verificando que `tasks`, `completed_ids` e `timeline` são atualizados exclusivamente pelos nodes.
- [ ] T017 [US2] Complementar `agente_tarefas/tests/test_cli.py` e `agente_tarefas/main.py` (smoke harness) com asserts/logs que conferem se o CLI apenas exibe dados provenientes do grafo.
- [ ] T018 [US2] Atualizar `specs/001-refactor-task-graph/quickstart.md` com instruções de execução dos testes automatizados e critérios de sucesso para validação do estado.

**Checkpoint**: Testes automatizados cobrem o fluxo completo e falhariam se o CLI voltasse a mutar estado internamente.

---

## Phase 5: User Story 3 - LangGraph CLI operators mirror the experience (Priority: P3)

**Goal**: Garantir que `langgraph run agente-tarefas` reproduz o mesmo comportamento do CLI customizado, permitindo execuções headless.
**Independent Test**: Executar `langgraph run agente-tarefas --thread-id demo --input ...` seguindo o quickstart e comprovar que `tasks`, `completed_ids` e `timeline` finais coincidem com o fluxo interativo.

### Implementation & Tests

- [ ] T019 [US3] Garantir que `agente_tarefas/graph.py` e `langgraph.json` aceitam payloads do LangGraph CLI (inputs/prompt_messages) documentando quaisquer parâmetros adicionais necessários.
- [ ] T020 [US3] Atualizar `agente_tarefas/docs/operations.md` com um passo-a-passo de `langgraph run agente-tarefas`, incluindo exemplos de payloads e interpretações do estado retornado.
- [ ] T021 [US3] Registrar em `specs/001-refactor-task-graph/quickstart.md` (seção LangGraph CLI) o resultado de um smoke test manual, com referências a logs/IDs para auditoria.

**Checkpoint**: Operadores podem usar LangGraph CLI para reproduzir toda a jornada, com documentação e exemplos.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalizar documentação, catálogos e verificações gerais.

- [ ] T022 Atualizar `PROJETOS.md` com o resumo funcional/técnico da refatoração de `agente_tarefas` (grafia e impacto nos nodes/testes).
- [ ] T023 [P] Rever `graph-nodes-patterns.md` e adicionar o padrão "graph-managed three-round workflow" se inexistente, garantindo que nomes e responsabilidades novos estejam catalogados.
- [ ] T024 Executar o checklist inteiro de `specs/001-refactor-task-graph/quickstart.md` (CLI, pytest, LangGraph CLI) e anexar evidências no PR/notas de release.

---

## Dependencies & Execution Order

1. **Phase 1** → 2 → 3 → 4 → 5 → 6 (sequencial). Nenhum trabalho de user story inicia antes de concluir a Fase 2.
2. **User Stories**: US1 é MVP e desbloqueia US2/US3. US2 (testes) e US3 (LangGraph CLI) podem ocorrer em paralelo após US1, desde que não haja conflitos de código.
3. **Task-level dependencies**: 
   - T008–T010 dependem de T004–T006.
   - T011 depende dos nodes T008–T010.
   - T012 depende de T011.
   - Testes T013–T017 dependem das implementações correspondentes.

### Parallel Execution Examples
- Durante a Fase 3, T008/T009/T010 podem ser executados em paralelo (nodes independentes) usando scaffolding comum.
- Na Fase 4, T015 e T016 podem ocorrer em paralelo (fixtures vs. integração) desde que compartilhem mocks consistentes.
- Na Fase 5, T020 (docs) e T021 (evidência) podem ser paralelos enquanto T019 garante suporte técnico.

## Implementation Strategy

1. **MVP (US1)**: Foque primeiro na movimentação total do estado para o grafo (nodes + CLI refactor + testes unitários). Once T008–T014 are complete, the CLI will already rely entirely on the graph.
2. **Hardening (US2)**: Immediately follow with strengthened pytest coverage and smoke validation so regressions are caught early.
3. **Operational Parity (US3)**: Finalize with LangGraph CLI parity and documentation so headless operators can rely on the same graph.
4. **Polish**: Update catalogs, patterns, and quickstart evidence before requesting review/merge.
