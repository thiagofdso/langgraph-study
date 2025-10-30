# Tasks: Iterative Reflection Agent Guidance

**Input**: Design documents from `/specs/014-add-reflection-agent/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Note**: Tasks reorganized para refletir o fluxo simplificado (arquivo único `main.py`).

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Criar `agente_reflexao_basica/` com `main.py` inicial e estrutura mínima necessária
- [X] T002 Copiar `.env` de `agente_simples/.env` para `agente_reflexao_basica/.env` sem alterações
- [X] T003 Registrar entrada preliminar em `PROJETOS.md` para o novo agente (será atualizada quando concluído)

---

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T004 Incorporar instruções de carregamento da chave Gemini e validação imediata no topo de `agente_reflexao_basica/main.py`

---

## Phase 3: User Story 1 - Refined Guidance Delivery (Priority: P1) 🎯 MVP

**Goal**: Gerar rascunhos e uma resposta final que incorporam feedback automático.

**Independent Test**: Executar `python agente_reflexao_basica/main.py` e verificar que o rascunho final cita ≥4 prioridades distintas e difere do rascunho inicial.

- [X] T005 [US1] Implementar função `generate` em `agente_reflexao_basica/main.py`
- [X] T006 [US1] Implementar função `reflect` em `agente_reflexao_basica/main.py`
- [X] T007 [US1] Montar o `StateGraph` com nós `generate` e `reflect` em `agente_reflexao_basica/main.py`
- [X] T008 [US1] Exibir todos os rascunhos e destacar a resposta final no console

---

## Phase 4: User Story 2 - Critique Transparency (Priority: P2)

**Goal**: Mostrar reflexões em ordem, permitindo auditoria rápida pelo console.

**Independent Test**: Ao rodar o script, cada reflexão aparece numerada antes do rascunho seguinte.

- [X] T009 [US2] Imprimir bloco “Reflexões” com cada reflexão numerada em `agente_reflexao_basica/main.py`
- [X] T010 [US2] Garantir ordenação cronológica entre reflexões e rascunhos no console

---

## Phase 5: User Story 3 - Iteration Control (Priority: P3)

**Goal**: Encerrar o fluxo automaticamente após atingir o limite embutido de ciclos.

**Independent Test**: Ajustar limite em `main.py`, rodar o script e confirmar que o número de reflexões não excede o limite.

- [X] T011 [US3] Implementar função `should_continue` com checagem `len(state["messages"]) > 6`
- [X] T012 [US3] Documentar no código como alterar o limite de reflexões

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T013 Atualizar `plan.md`, `spec.md` e `quickstart.md` para refletir a arquitetura de arquivo único
- [X] T014 Revisar `PROJETOS.md` descrevendo a abordagem final baseada em `StateGraph`
- [X] T015 Normalizar formatação e mensagens de console em `agente_reflexao_basica/main.py`

---

## Dependencies & Execution Order

- Setup (Phase 1) → Fundamentos (Phase 2) → US1 → US2 → US3 → Polish.
- US1 habilita US2 e US3; estas fases dependem das funções definidas anteriormente.

## Parallel Execution Opportunities

- Ajustes documentais (T013–T015) podem ocorrer em paralelo após US3.
- Dentro da Fase 3, funções `generate` e `reflect` podem ser desenvolvidas em paralelo após T004.

## MVP Scope

- Completar a Fase 3 (US1) entrega uma resposta final iterativamente refinada.
