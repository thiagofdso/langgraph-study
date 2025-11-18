# Tasks: Refatorar agente_mcp

**Input**: Design documents from `/specs/001-refactor-agente-mcp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar arquivos e configurações base exigidos pela constituição antes da refatoração.

- [X] T001 Copiar `agente_simples/.env` como base e publicar `agente_mcp/.env.example`
- [X] T002 Registrar o grafo `agente_mcp/graph.py:create_graph` adicionando entrada incremental em `langgraph.json`
- [X] T003 [P] Criar diretório `agente_mcp/docs/` com README inicial descrevendo propósito do agente

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Estruturar módulos core (`config`, `state`, `utils`, `graph`) que suportam todos os user stories.

- [X] T004 Implementar `AppConfig` e carregamento de `.env` em `agente_mcp/config.py`
- [X] T005 Definir `AgentSession` e reducers em `agente_mcp/state.py`
- [X] T006 [P] Configurar logger estruturado e helpers em `agente_mcp/utils/logging.py`
- [X] T007 [P] Definir `ServerProfile` básico + validadores em `agente_mcp/utils/servers.py`
- [X] T008 Organizar exports em `agente_mcp/utils/__init__.py` e remover uso antigo de `agent_graph.py`
- [X] T009 Criar esqueleto de `agente_mcp/graph.py` com `create_graph` retornando `StateGraph` vazio e docstring

**Checkpoint**: Estrutura modular concluída; é possível importar config/state/graph sem efeitos colaterais.

---

## Phase 3: User Story 1 - Operar agente multi-servidor via comando único (Priority: P1) 🎯 MVP

**Goal**: Permitir que `python agente_mcp/main.py` valide configuração, inicialize servidores e execute perguntas padrão produzindo logs ordenados.

**Independent Test**: Seguir `specs/001-refactor-agente-mcp/quickstart.md` → configurar `.env`, iniciar servidores declarados e executar `PYTHONPATH=. python agente_mcp/main.py`; verificar que todas as mensagens e tool-calls são impressas em ordem cronológica e que processos auto-start encerram automaticamente.

### Implementation

- [X] T010 [P] [US1] Implementar nodes `validate_input`, `invoke_llm`, `execute_tools`, `format_response`, `handle_error` em `agente_mcp/utils/nodes.py`
- [X] T011 [US1] Conectar nodes no `StateGraph` em `agente_mcp/graph.py`, incluindo checkpointer configurável e binding com `MultiServerMCPClient`
- [X] T012 [US1] Refatorar `agente_mcp/main.py` para carregar `AppConfig`, iniciar/parar servidores declarados e chamar `graph.invoke` com perguntas configuráveis
- [X] T013 [P] [US1] Adicionar coleta de `run_log` + registros estruturados por tool-call em `agente_mcp/main.py` e `agente_mcp/utils/logging.py`
- [ ] T014 [US1] Atualizar `agente_mcp/README.md` com passos detalhados (setup, execução, troubleshooting) alinhados ao Quickstart
- [ ] T015 [US1] Alinhar `specs/001-refactor-agente-mcp/quickstart.md` ao comportamento real (perguntas padrão, flags `auto_start`)

**Checkpoint**: `main.py` executa fluxo completo com math/weather, valida `.env`, gera logs e encerra dependências automaticamente.

---

## Phase 4: User Story 2 - Adicionar novo servidor MCP sem retrabalho (Priority: P2)

**Goal**: Permitir que mantenedores cadastrem/removam servidores apenas editando perfis declarativos, sem tocar no grafo.

**Independent Test**: Criar stub `agente_mcp/mcp_servers/sample_server.py`, adicioná-lo ao arquivo de perfis, executar `python agente_mcp/main.py` e verificar que o novo servidor aparece na lista de ferramentas e responde sem ajustes adicionais.

### Implementation

- [ ] T016 [P] [US2] Estender `agente_mcp/utils/servers.py` para carregar perfis de `agente_mcp/config/servers.yaml` com validações de transporte/duplicidade
- [ ] T017 [US2] Criar `agente_mcp/config/servers.yaml` com exemplos (math, weather, placeholder custom) e instruções inline
- [ ] T018 [US2] Atualizar `agente_mcp/main.py` para reagir dinamicamente a servidores habilitados/desabilitados (inclusive remoção temporária)
- [ ] T019 [US2] Documentar tutorial “Adicionar novo servidor” em `agente_mcp/docs/servers.md` referenciando YAML e passos de QA manual
- [ ] T020 [US2] Garantir que `agente_mcp/graph.py` e logs exibam nomes de ferramentas/servidores vindos do perfil declarativo, recusando conflitos antes da execução

**Checkpoint**: Novo servidor pode ser adicionado/removido editando apenas o YAML + script correspondente, e erros são relatados antes de iniciar o grafo.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Consolidar documentação, catálogo de projetos e padrões compartilhados.

- [ ] T021 Atualizar `PROJETOS.md` com descrição funcional/técnica do agente refatorado
- [ ] T022 Registrar novos nodes/responsabilidades em `graph-nodes-patterns.md`
- [ ] T023 [P] Revisar `langgraph.json` e `agente_mcp/docs/README.md` após execução do quickstart para assegurar consistência
- [ ] T024 Executar o roteiro descrito em `specs/001-refactor-agente-mcp/quickstart.md` e anotar resultados/ajustes necessários

---

## Dependencies & Execution Order

1. **Phase 1 → Phase 2**: Setup precisa concluir antes da criação dos módulos.
2. **Phase 2 → US1/US2**: A base modular habilita desenvolvimento paralelo das histórias.
3. **US1 → US2**: US2 depende de `main.py` e `graph.py` estáveis, portanto inicia após o checkpoint de US1.
4. **Polish** depende da conclusão das histórias planejadas.

### Parallel Opportunities
- **Setup/Foundational**: T003, T006 e T007 são independentes (docs, logging, server profiles).
- **US1**: T010 (nodes) e T013 (logging hooks) podem acontecer em paralelo antes de T011/T012; T014 e T015 podem ser feitas em paralelo após T012.
- **US2**: T016 (loader) e T019 (docs) podem começar simultaneamente; T017 depende de decisão de formato mas não bloqueia T020.
- **Cross-story**: Após Phase 2, US1 e US2 podem progredir em paralelo desde que alterações em `main.py` sejam coordenadas via branch review.

## Implementation Strategy

1. **MVP (US1)**: Concluir fases 1–3 para obter execução manual confiável; esta entrega já atende SC-001/SC-003.
2. **Extensibilidade (US2)**: Introduzir YAML declarativo e documentação para permitir novos servidores sem retrabalho.
3. **Polish**: Atualizar catálogos (`PROJETOS.md`, `graph-nodes-patterns.md`) e validar o quickstart ponta a ponta.
