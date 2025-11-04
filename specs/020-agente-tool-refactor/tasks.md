---

description: "Task list for refatorar agente_tool"
---

# Tasks: Refatorar agente_tool

**Input**: Design documents from `/specs/020-agente-tool-refactor/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Note**: This task list é parte do fluxo `.specify`, garantindo rastreabilidade e execução incremental.

**Tests**: Incluir testes conforme solicitado na especificação (validação, ferramenta, integração).

**Organização**: Tarefas agrupadas por user story para permitir entregas independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Executar em paralelo (arquivos distintos, sem dependências).
- **[Story]**: User story associada (US1, US2, US3).
- Descrições incluem caminhos de arquivo exatos.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar baseline e estruturas comuns antes da refatoração.

- [X] T001 Registrar comportamento atual do agente em `agente_tool/docs/baseline.md` executando `python agente_tool/main.py`.
- [X] T002 Criar diretórios `agente_tool/docs/` e `agente_tool/tests/` com arquivos vazios de inicialização (`__init__.py`) para documentação e testes.
- [X] T003 Adicionar `agente_tool/.env.example` com placeholders de credenciais e atualizar instruções no topo do arquivo.
- [X] T004 Atualizar `requirements.txt` garantindo dependências `langgraph`, `langchain-core`, `langchain_google_genai`, `python-dotenv`, `pytest`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Componentes compartilhados que abastecem todas as user stories.

- [X] T005 Implementar `agente_tool/config.py` com `AppConfig`, criação de LLM Gemini e `MemorySaver`.
- [X] T006 Definir `GraphState` e `ThreadConfig` em `agente_tool/state.py` conforme data-model.md.
- [X] T007 Criar `agente_tool/utils/logging.py` expondo `get_logger` consistente com agentes de referência.
- [X] T008 Configurar `agente_tool/tests/conftest.py` com fixtures para `create_app` e estado inicial.

---

## Phase 3: User Story 1 - Estrutura modular consistente (Priority: P1) 🎯

**Goal**: Reorganizar `agente_tool` seguindo padrões de estrutura e nomenclatura.

**Independent Test**: Confirmar que `agente_tool.graph.create_app` compila e que `graph-nodes-patterns.md` lista todos os nodes usados pelo agente.

### Implementation

- [X] T009 [US1] Criar `agente_tool/utils/__init__.py` reexportando `nodes`, `tools`, `logging` e constantes necessárias.
- [X] T010 [US1] Migrar funções de validação, planejamento, execução de ferramentas, invocação de LLM e formatação para `agente_tool/utils/nodes.py` com docstrings.
- [X] T011 [US1] Portar a ferramenta calculadora existente para `agente_tool/utils/tools.py` (mantendo comportamento original).
- [X] T012 [US1] Construir o grafo em `agente_tool/graph.py` adicionando nodes `validate_input`, `plan_tool_usage`, `invoke_model`, `execute_tools`, `format_response`.
- [X] T013 [US1] Atualizar `agente_tool/__init__.py` para exportar `create_app`.
- [X] T014 [US1] Implementar CLI em `agente_tool/cli.py` com comando `run` acionando `create_app`.
- [X] T015 [US1] Ajustar `agente_tool/main.py` para delegar à CLI.
- [X] T016 [US1] Acrescentar entrada `"agente-tool"` a `langgraph.json` preservando registros existentes.
- [X] T017 [US1] Atualizar `graph-nodes-patterns.md` com registros de `plan_tool_usage` e `execute_tools` apontando para arquivos do `agente_tool`.

---

## Phase 4: User Story 2 - Fluxo funcional preservado (Priority: P2)

**Goal**: Garantir que o agente continue respondendo perguntas matemáticas com uso seguro da ferramenta.

**Independent Test**: Executar fluxo “quanto é 300 dividido por 4?” obtendo `Resposta do agente: 75`.

### Tests (obrigatórios)

- [X] T018 [P] [US2] Criar teste de integração em `agente_tool/tests/test_graph.py` validando chamada da ferramenta e resposta final.
- [X] T019 [P] [US2] Criar testes de unidade em `agente_tool/tests/test_nodes.py` cobrindo validação de input, planejamento da ferramenta e formatação.

### Implementation

- [X] T020 [US2] Endurecer `calculator` em `agente_tool/utils/tools.py` usando `ast.parse` com sandbox e mensagens de erro amigáveis.
- [X] T021 [US2] Implementar lógica de `plan_tool_usage` em `agente_tool/utils/nodes.py` populando `tool_plans` e status adequados.
- [X] T022 [US2] Implementar `execute_tools` em `agente_tool/utils/nodes.py` consumindo `calculator` e anexando mensagens ao estado.
- [X] T023 [US2] Ajustar `invoke_model` em `agente_tool/utils/nodes.py` para usar `config.create_llm()` e tratar exceções.
- [X] T024 [US2] Refinar `agente_tool/graph.py` para adicionar edges condicionais roteando entre ferramenta e LLM.

---

## Phase 5: User Story 3 - Observabilidade e qualidade asseguradas (Priority: P3)

**Goal**: Disponibilizar documentação, logs e trilha de auditoria completos.

**Independent Test**: Revisar `agente_tool/docs/` e executar `pytest` garantindo logs informativos nas etapas principais.

### Tests (opcionais)

- [X] T025 [P] [US3] Adicionar asserções de logging em `agente_tool/tests/test_nodes.py` cobrindo caminhos de sucesso e erro.

### Implementation

- [X] T026 [US3] Instrumentar `agente_tool/utils/nodes.py` com logs `info`/`warning` usando `get_logger`.
- [X] T027 [US3] Documentar arquitetura atualizada em `agente_tool/docs/architecture.md`, incluindo diagrama textual do fluxo.
- [X] T028 [US3] Atualizar `agente_tool/docs/baseline.md` com execução pós-refatoração demonstrando CLI.
- [X] T029 [US3] Revisar `agente_tool/README.md` e `specs/020-agente-tool-refactor/quickstart.md` para refletir CLI e passos de teste.

---

## Phase N: Polish & Cross-Cutting Concerns

- [X] T030 Executar `ruff check agente_tool` e `pytest agente_tool/tests -v`.
- [X] T031 Garantir formatação (`black agente_tool`) e remover artefatos (`__pycache__`).
- [X] T032 Validar `graph-nodes-patterns.md` garantindo 100% dos nodes documentados e consistentes.
- [X] T033 Atualizar `PROJETOS.md` com resumo da refatoração e lições aprendidas.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Nenhuma dependência.
- **Foundational (Phase 2)**: Depende da conclusão da Fase 1.
- **User Stories (Phase 3–5)**: Cada fase depende das anteriores; US2 e US3 requerem conclusão da Fase 3.
- **Polish (Phase N)**: Depende de todas as user stories concluídas.

### User Story Dependencies

- **US1 (P1)**: Base para US2 e US3.
- **US2 (P2)**: Requer US1 completo; independente de US3.
- **US3 (P3)**: Requer US1 e US2 para capturar logs e documentação.

### Parallel Opportunities

- Testes T018, T019 e T025 podem ser executados em paralelo após os respectivos módulos estarem prontos.
- Documentação T027 e T028 podem ocorrer em paralelo após estabilização do fluxo.

---

## Implementation Strategy

### MVP (User Story 1)
1. Concluir Fases 1 e 2.
2. Implementar todas as tarefas da US1.
3. Validar `create_app` compilado e catalogação de nodes.

### Incremental Delivery
1. **Entrega 1**: MVP (estrutura modular pronta).
2. **Entrega 2**: Completar US2 garantindo comportamento funcional e testes.
3. **Entrega 3**: US3 adicionando observabilidade e documentação.
4. **Finalização**: Fase de Polish para ajustes finais, lint e atualização de catálogo.

### Parallel Example – US2
```bash
# Em terminais separados:
pytest agente_tool/tests/test_nodes.py::test_plan_tool_usage
pytest agente_tool/tests/test_graph.py::test_calculator_flow
```

---
