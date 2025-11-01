
# Tasks: Refactor Memory Agent

**Input**: Design documents from `/specs/019-refactor-memoria-agent/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Note**: This task list is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear task generation and alignment with project goals.

**Tests**: Test tasks are included where the specification mandates verificação automatizada (FR-007, SC-004).

**Organization**: Tasks are grouped por história de usuário para permitir implementação e validação independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode ser executado em paralelo (arquivos diferentes, nenhuma dependência pendente)
- **[Story]**: História de usuário a que a tarefa pertence (US1, US2, US3)
- Cada tarefa inclui caminho de arquivo explícito

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar a estrutura básica do projeto e arquivos de configuração compartilhados.

- [x] T001 Criar scaffolding do pacote `agente_memoria` (agente_memoria/utils/__init__.py, agente_memoria/tests/__init__.py, agente_memoria/docs/)
- [x] T002 Copiar modelo de ambiente para agente_memoria/.env.example a partir de agente_simples/.env.example
- [x] T003 [P] Registrar o grafo refatorado em langgraph.json apontando para agente_memoria/graph.py:create_app

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura núcleo que deve estar pronta antes de iniciar histórias de usuário.

**⚠️ CRITICAL**: Nenhuma história pode começar antes desta fase concluir.

- [x] T004 Definir GraphState e validações auxiliares em agente_memoria/state.py
- [x] T005 Implementar AppConfig, criação de LLM/checkpointer e preflight base em agente_memoria/config.py
- [x] T006 [P] Criar utilitário de logging alinhado ao padrão do agente simples em agente_memoria/utils/logging.py
- [x] T007 [P] Criar módulo agente_memoria/utils/nodes.py com docstrings e assinaturas placeholder para nós
- [x] T008 Atualizar agente_memoria/main.py para delegar execução para agente_memoria/cli.py.main com docstring

**Checkpoint**: Fundamentos prontos – histórias de usuário podem iniciar.

---

## Phase 3: User Story 1 - Conversa com memória persistente (Priority: P1) 🎯 MVP

**Goal**: Permitir diálogo multi-turno via CLI reutilizando histórico por thread.

**Independent Test**: Executar `python -m agente_memoria --thread teste`, enviar duas perguntas encadeadas e confirmar que a segunda resposta referencia o conteúdo da primeira sem reconfiguração manual.

### Implementation for User Story 1

- [x] T009 [P] [US1] Definir prompts e mensagens padrão para memória em agente_memoria/prompts.py
- [x] T010 [P] [US1] Implementar `validate_question_node` com Pydantic em agente_memoria/utils/nodes.py
- [x] T011 [P] [US1] Implementar `load_history_node` para recuperar histórico do checkpointer em agente_memoria/utils/nodes.py
- [x] T012 [P] [US1] Implementar `invoke_model_node` utilizando AppConfig.create_llm em agente_memoria/utils/nodes.py
- [x] T013 [P] [US1] Implementar `update_memory_node` preservando sequências em agente_memoria/utils/nodes.py
- [x] T014 [US1] Implementar `format_response_node` com cálculo de duração e status em agente_memoria/utils/nodes.py
- [x] T015 [US1] Montar fluxo StateGraph completo em agente_memoria/graph.py ligando nós e checkpointer
- [x] T016 [US1] Construir CLI interativa com suporte a thread_id inicial em agente_memoria/cli.py
- [x] T017 [US1] Criar teste de integração multi-turno validando memória em agente_memoria/tests/test_graph.py
- [x] T018 [US1] Criar testes unitários para nós de validação e atualização de histórico em agente_memoria/tests/test_nodes.py

**Checkpoint**: História 1 funcional e testável de forma independente.

---

## Phase 4: User Story 2 - Diagnóstico guiado de configuração (Priority: P2)

**Goal**: Bloquear execução sem credenciais e orientar correções com mensagens amigáveis.

**Independent Test**: Remover `GEMINI_API_KEY`, executar `python -m agente_memoria --check` e verificar mensagem clara de bloqueio com instrução de correção.

### Implementation for User Story 2

- [x] T019 [US2] Integrar preflight de configuração e atalhos `--check` na inicialização CLI em agente_memoria/cli.py
- [x] T020 [US2] Enriquecer `invoke_model_node` com mensagens de erro amigáveis e categorização em agente_memoria/utils/nodes.py
- [x] T021 [US2] Adicionar testes cobrindo falhas de credencial e parâmetros inválidos em agente_memoria/tests/test_config.py

**Checkpoint**: História 2 pronta com bloqueios e diagnósticos independentes.

---

## Phase 5: User Story 3 - Operação observável e sustentável (Priority: P3)

**Goal**: Fornecer observabilidade, comandos operacionais e documentação para manutenção.

**Independent Test**: Executar o agente, emitir `/reset` e verificar logs em agente_memoria/logs/agent.log contendo thread, pergunta e status; confirmar que histórico é limpo e documentado em operações.

### Implementation for User Story 3

- [x] T022 [P] [US3] Instrumentar logging estruturado em agente_memoria/utils/nodes.py e agente_memoria/cli.py
- [x] T023 [US3] Implementar comandos `/reset` e `/thread` com limpeza segura do histórico em agente_memoria/cli.py
- [x] T024 [US3] Estender testes para cobrir reset de thread e captura de logs em agente_memoria/tests/test_graph.py
- [x] T025 [US3] Escrever guia de operações, troubleshooting e fluxo de logs em agente_memoria/docs/operations.md
- [x] T026 [US3] Atualizar instruções de uso e logs em agente_memoria/README.md

**Checkpoint**: Histórias 1–3 independentes e auditáveis.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Ajustes finais, documentação e validações globais.

- [x] T027 [P] Executar suíte `pytest agente_memoria/tests -v` e capturar resultados no planejamento
- [x] T028 [P] Validar passo a passo de specs/019-refactor-memoria-agent/quickstart.md e ajustar se necessário
- [x] T029 Atualizar PROJETOS.md com resumo funcional e abordagem técnica do agente_memoria refatorado

---

## Dependencies & Execution Order

- **Phase 1 → Phase 2**: Setup deve preceder fundações para garantir estrutura de pastas e arquivos base.
- **Phase 2 → US1/US2/US3**: Histórias dependem de estado/config/logging prontos; após Phase 2, US1 inicia (MVP).
- **User Story Dependencies**:
  - US1 (P1) não depende de outras histórias e pode iniciar imediatamente após Phase 2.
  - US2 (P2) depende de US1 apenas para reutilizar CLI; implementável em paralelo após US1 concluir CLI básica.
  - US3 (P3) depende de US1 (gera logs a partir do fluxo) e de US2 (mensagens de diagnóstico reutilizadas).
- **Polish (Phase 6)**: Executar após histórias desejadas estarem concluídas.

## Parallel Execution Opportunities

- Phase 1: T003 pode ocorrer em paralelo após criação de diretórios.
- Phase 2: T006 e T007 podem avançar em paralelo enquanto T004/T005 são concluídos.
- US1: T009–T013 podem ser divididos entre membros diferentes após skeleton de nodes pronto; T017 e T018 rodam em paralelo após implementação.
- US3: T022 pode iniciar em paralelo com T023 após CLI básica pronta.
- Phase 6: T027 e T028 são independentes e podem ser executados simultaneamente.

## Implementation Strategy (MVP First)

1. **MVP (US1)**: Completar Phases 1–3 para entregar conversas multi-turno com memória e testes correspondentes.
2. **Enhanced Diagnostics (US2)**: Adicionar bloqueios de configuração e mensagens orientativas.
3. **Operational Maturity (US3)**: Incorporar logging, comandos administrativos e documentação.
4. **Polish**: Validar quickstart, atualizar PROJETOS.md e garantir qualidade geral.
