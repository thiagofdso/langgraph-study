# Tasks: Simplified Code Generation Loop

**Input**: Design documents from `/specs/015-auto-code-agent/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

## Phase 1: Setup

- [X] T001 Criar estrutura inicial em `agente_codigo/main.py` com constantes (`MAX_ITERATIONS = 5`), estado tipado do LangGraph e registrador de memória (`InMemorySaver`).

## Phase 2: Tests & Instrumentation

- [X] T002 Definir comando manual de verificação (`python agente_codigo/main.py`) e documentar como capturar stdout/stderr para inspeção.

## Phase 3: User Story 1 – Loop de Geração e Execução (Priority: P1)

- [X] T003 Implementar nó de geração em `agente_codigo/main.py` utilizando `gemini-2.5-flash`, aceitando histórico + feedback da reflexão, atualizando contador e armazenando string de código.
- [X] T004 Implementar nó de execução que avalia o código em memória (via `exec`) e registra resultados (`stdout`, `stderr`, exceções) no estado.
- [X] T005 Conectar grafo (`StateGraph`) com fluxo `gerar -> executar -> decidir`, garantindo entrada com prompt de teste definido no spec.

## Phase 4: User Story 2 – Correção Orientada por Reflexão (Priority: P1)

- [X] T006 Implementar nó de reflexão em `agente_codigo/main.py` que recebe código atual + mensagem de erro e gera feedback separado usando `gemini-2.5-flash`.
- [X] T007 Ajustar atualização de estado para armazenar feedback tanto no histórico (para geração) quanto em variável dedicada à reflexão.
- [X] T008 Adicionar impressão no console resumindo erros e feedback quando reflexão é acionada.

## Phase 5: User Story 3 – Controle Seguro do Ciclo (Priority: P2)

- [X] T009 Implementar nó de decisão que encerra quando `return_code == 0` ou `iteration_count >= 5`, encaminhando para reflexão quando houver erro.
- [X] T010 Garantir que o fluxo final imprime o código da última geração e motivo de encerramento (sucesso, limite atingido ou erro fatal).

## Phase 6: Polish & Documentation

- [X] T011 Atualizar `specs/015-auto-code-agent/quickstart.md` com instruções para executar o agente em memória e interpretar saídas.
- [X] T012 Atualizar `agente_codigo/README.md` (ou documento equivalente) descrevendo o fluxo simplificado e limitações atuais (sem escrita em disco).
- [X] T013 Registrar atualizações relevantes em `PROJETOS.md`, incluindo nota sobre o agente in-memory e limite de 5 iterações.
