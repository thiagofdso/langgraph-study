# Tasks: Agente com Aprovação Humana

**Input**: Design documents from `/specs/017-approval-agent-flow/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Note**: This task list é parte do fluxo specification-driven do `.specify`, garantindo alinhamento entre requisitos e execução.

**Tests**: Apenas verificação manual executando `python agente_aprovacao/main.py`, conforme plano. Nenhum teste automatizado requerido.

**Organization**: Tarefas agrupadas por história de usuário para permitir implementação e validação independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Execução paralela segura (arquivos distintos e sem dependências pendentes)
- **[Story]**: História de usuário (US1, US2, US3)
- Sempre incluir caminhos de arquivo na descrição

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicializar projeto `agente_aprovacao` com estrutura mínima e variáveis de ambiente.

- [X] T001 Criar diretório `agente_aprovacao/` com `__init__.py` e `main.py` esqueleto conforme plano
- [X] T002 Copiar `agente_web/.env` para `agente_aprovacao/.env`, mantendo variáveis intactas

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Preparar estado compartilhado, recursos externos e grafo LangGraph antes das histórias.

**⚠️ CRITICAL**: Nenhuma história pode iniciar antes desta fase concluir.

- [X] T003 Definir `ApprovalSessionState` e auxiliares em `agente_aprovacao/main.py` segundo data-model.md
- [X] T004 Configurar carregamento de `.env`, instanciar `ChatGoogleGenerativeAI` e `TavilySearch` reutilizando parâmetros de `agente_web` em `agente_aprovacao/main.py`
- [X] T005 Implementar `build_graph()` em `agente_aprovacao/main.py` com registro dos nós `gerar_resposta`, `aprovacao_humana`, `busca_internet`, `END` e checkpointer `InMemorySaver`

---

## Phase 3: User Story 1 - Aprovar uso de ferramentas (Priority: P1) 🎯 MVP

**Goal**: Garantir que qualquer execução de ferramenta externa seja precedida por aprovação humana explícita.

**Independent Test**: Rodar `python agente_aprovacao/main.py`, aprovar o uso da pesquisa e confirmar que a resposta final só aparece após a decisão registrada e retorno da Tavily.

### Implementation for User Story 1

- [X] T006 [US1] Implementar lógica inicial de `gerar_resposta` em `agente_aprovacao/main.py` para preparar resumo da ação, definir `approval_required` e encaminhar ao nó de aprovação
- [X] T007 [US1] Implementar nó `aprovacao_humana` em `agente_aprovacao/main.py` usando `interrupt` e payload inspirado em `agente_perguntas/main.py`
- [X] T008 [US1] Atualizar `agente_aprovacao/main.py` para tratar eventos `interrupt`, coletar decisão humana e retomar o grafo com `Command(resume=...)`
- [X] T009 [US1] Implementar nó `busca_internet` em `agente_aprovacao/main.py` invocando Tavily e armazenando resultados em `search_results`

**Checkpoint**: Fluxo aprovado chama a ferramenta, registra decisão e gera resposta com dados pesquisados.

---

## Phase 4: User Story 2 - Validar entrada do usuário (Priority: P2)

**Goal**: Garantir que entradas incompletas sejam corrigidas antes de prosseguir para aprovação e execução de ferramentas.

**Independent Test**: Rodar `python agente_aprovacao/main.py`, fornecer entrada inválida, verificar retorno com mensagens de correção, reenviar dados válidos e confirmar continuação do fluxo.

### Implementation for User Story 2

- [X] T010 [US2] Criar função de validação em `agente_aprovacao/main.py` para popular `validation_errors`, normalizar `ValidatedSubmission` e controlar `validation_attempts`
- [X] T011 [US2] Ajustar `gerar_resposta` em `agente_aprovacao/main.py` para interromper quando houver erros, solicitando novos dados e reiniciando o nó após correção
- [X] T012 [US2] Atualizar `agente_aprovacao/main.py` para coletar entradas corrigidas durante a retomada, aplicar limite de tentativas e finalizar com aviso quando excedido

**Checkpoint**: Fluxo lida com entradas inválidas sem encerrar a sessão e só avança com dados aprovados.

---

## Phase 5: User Story 3 - Responder sem ferramenta aprovada (Priority: P3)

**Goal**: Permitir que o agente entregue resposta alternativa quando a pesquisa externa for negada.

**Independent Test**: Rodar `python agente_aprovacao/main.py`, negar a aprovação da pesquisa, confirmar retorno ao nó inicial, geração de resposta sem Tavily e encerramento imediato.

### Implementation for User Story 3

- [X] T013 [US3] Estender `aprovacao_humana` em `agente_aprovacao/main.py` para registrar decisões negativas, atualizar `notes` e direcionar fluxo para resposta final sem ferramenta
- [X] T014 [US3] Atualizar `gerar_resposta` em `agente_aprovacao/main.py` para compor resposta final com `response_stage == "final"` e indicar quando nenhuma ferramenta foi usada
- [X] T015 [US3] Ajustar `agente_aprovacao/main.py` para exibir avisos sobre respostas sem ferramenta e encerrar execução após segunda passagem pelo nó

**Checkpoint**: Cenários sem aprovação resultam em resposta interna clara e encerramento do fluxo.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalizar documentação, catalogação e validação manual completa.

- [X] T016 Criar `agente_aprovacao/README.md` descrevendo fluxo, aprovação humana e cenários de fallback
- [X] T017 Registrar resultados de verificação manual (aprovação, reprovação, validação) em `specs/017-approval-agent-flow/quickstart.md`
- [X] T018 Atualizar `PROJETOS.md` com resumo funcional e abordagem técnica do agente de aprovação

---

## Dependencies & Execution Order

- **Phase 1** → **Phase 2** → **User Story Phases** → **Polish**. Nenhuma história inicia antes da Fase 2.
- **User Story Order**: US1 (P1) é MVP e habilita fluxo principal; US2 (P2) depende de US1 pronto para validar entradas antes da aprovação; US3 (P3) depende de US1 para aproveitar o nó de aprovação e de US2 para reutilizar estado já validado.
- **Task Dependencies**:
  - T006–T009 dependem de T003–T005 concluídos.
  - T010–T012 dependem de T006–T008 para garantir integração correta.
  - T013–T015 dependem de T006–T012 para aproveitar estados e condicional final.
  - T017 depende da implementação completa das histórias para documentar cenários.

---

## Parallel Execution Opportunities

- Durante Fase 1, T001 e T002 podem ocorrer em paralelo se desejado, pois atuam em arquivos distintos.
- Na Fase 2, atividades são sequenciais (mesmo arquivo), portanto não paralelizar.
- Em US1, T008 (CLI) pode avançar após T006–T007 enquanto T009 (Tavily) progride, desde que coordene pontos de integração.
- US2 e US3 devem ocorrer após conclusão das fases anteriores; dentro de cada história o trabalho é sequencial devido a dependências no mesmo módulo.
- Fase de Polish: T016–T018 podem ser divididos entre membros diferentes após todas as histórias estarem aprovadas.

---

## Implementation Strategy

1. **MVP (US1)**: Entregar fluxo com aprovação humana e uso da ferramenta web somente após consentimento. Permite validação do conceito principal antes das demais histórias.
2. **Iteração 2 (US2)**: Adicionar validação iterativa para entradas, reforçando qualidade dos dados antes de solicitar aprovação.
3. **Iteração 3 (US3)**: Completar fallback sem ferramenta para cenários restritivos, garantindo conformidade.
4. **Polish**: Atualizar documentação oficial, catálogo `PROJETOS.md` e registrar testes manuais para auditoria.
