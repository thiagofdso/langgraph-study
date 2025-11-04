---
description: "Task list for migrating agente_tool tool execution to ToolNode"
---

# Tasks: Migrar agente_tool para ToolNode

**Input**: `specs/020-agente-tool-refactor/spec.md`, `agente_tool/docs/architecture.md`, `agente_tool/utils/nodes.py`, `agente_tool/graph.py`

**Prerequisites**: `specs/020-agente-tool-refactor/plan.md`, `specs/020-agente-tool-refactor/research.md`, `graph-nodes-patterns.md`, contratos vigentes em `specs/020-agente-tool-refactor/contracts/`

**Tests alvo**: `pytest agente_tool/tests -v`, `ruff check agente_tool`

**Organização**: Tarefas agrupadas por user stories focadas em adoção do `ToolNode` e garantia de regressão zero.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode executar em paralelo (sem compartilhamento de arquivos).
- **[Story]**: US1 (Adoção ToolNode), US2 (Qualidade & Paridade), US3 (Documentação & Governança).
- Descrições incluem arquivos/caminhos exatos e expectativa de entrega.

---

## Phase 0: Diagnóstico e Planejamento

**Objetivo**: Consolidar entendimento do fluxo atual baseado em `partial` e preparar plano de migração.

- [ ] T201 [US1] Levantar uso de `functools.partial` em `agente_tool/graph.py` e sintetizar dependências no novo `specs/021-agente-tool-toolnode/research.md` (trecho dedicado a “Motivação para ToolNode”).
- [ ] T202 [US1] Registrar comportamento atual do nó `execute_tools` (mensagens adicionadas, campos do estado mutados) anexando um fluxo de referência em `agente_tool/docs/baseline.md` (seção “Antes da migração ToolNode”).

---

## Phase 1: Estado e Nós (US1 – Adoção ToolNode)

**Objetivo**: Preparar o estado e nodes para trabalhar com a saída nativa do `ToolNode`.

- [ ] T205 [US1] Atualizar `agente_tool/state.py` introduzindo `pending_tool_calls: list[ToolCall] | None` (TypedDict) e `last_tool_run: dict[str, Any] | None`, garantindo compatibilidade com checkpoints existentes.
- [ ] T206 [US1] Refatorar `plan_tool_usage` em `agente_tool/utils/nodes.py` para popular `pending_tool_calls` (lista) a partir de `AIMessage.tool_calls`, mantendo logs e mensagens de erro atuais.
- [ ] T207 [US1] Substituir `execute_tools` por um novo node `handle_tool_result` que:
  - Consome o último `ToolMessage` gerado pelo `ToolNode`.
  - Atualiza `metadata["last_tool_result"]`, `metadata["last_tool_expression"]`, `last_tool_run` e `resposta`.
  - Normaliza status para `STATUS_VALIDATED` ou `STATUS_ERROR` conforme presença de exceções no `ToolNode`.
- [ ] T208 [US1] Expor novos utilitários em `agente_tool/utils/__init__.py` (remove export de `execute_tools`, adiciona `handle_tool_result`).

---

## Phase 2: Grafo e Roteamento (US1 – Adoção ToolNode)

**Objetivo**: Introduzir `ToolNode` e eliminar dependência de `partial` para ferramentas.

- [ ] T210 [US1] Instanciar `ToolNode([calculator])` em `agente_tool/graph.py`, importando `ToolNode` e `tools_condition` de `langgraph.prebuilt`.
- [ ] T211 [US1] Ajustar roteamento:
  - `invoke_model` → `tools_condition` com mapeamento `{ "tools": "tools", END: "format_response" }`.
  - `tools` → `handle_tool_result` → `finalize_response`.
  - Atualizar `_route_after_validation`/`_route_after_tools` conforme necessário para manter finais de fluxo.
- [ ] T212 [US1] Permitir injeção de ferramentas em `create_app` adicionando parâmetro opcional `tools: Sequence[BaseTool] | None`; usar fallback `[calculator]` para manter compatibilidade com testes e CLI.
- [ ] T213 [US1] Remover uso de `partial` para tool execution e garantir que `calc_runner` não seja mais necessário (limpar código morto e logs associados).
- [ ] T214 [US1] Atualizar `graph-nodes-patterns.md` documentando `handle_tool_result` e o uso de `ToolNode` (seção padrões de ferramentas).

---

## Phase 3: Testes e Qualidade (US2 – Garantir Paridade)

**Objetivo**: Adaptar suíte de testes e validar regressão zero.

- [ ] T220 [US2] Atualizar `agente_tool/tests/test_nodes.py`:
  - Ajustar testes que chamavam `execute_tools` para o novo `handle_tool_result`.
  - Adicionar caso cobrindo múltiplos `ToolMessage` retornados pelo `ToolNode`.
  - Verificar que `pending_tool_calls` é limpo/consumido após processamento.
- [ ] T221 [US2] Adaptar `agente_tool/tests/test_graph.py` para injetar ferramentas falsas via novo parâmetro `tools` e confirmar que o nó `tools` é instância de `ToolNode`.
- [ ] T222 [US2] Introduzir teste cobrindo cenário de erro da ferramenta (ex.: `CalculatorError`) validando mensagem ao usuário e status `STATUS_ERROR`.
- [ ] T223 [P] [US2] Rodar `pytest agente_tool/tests -v` documentando saída em `specs/021-agente-tool-toolnode/research.md` (seção “Resultados de testes”).

---

## Phase 4: Documentação e Governança (US3)

**Objetivo**: Atualizar documentação operacional e artefatos compartilhados.

- [ ] T230 [US3] Revisar `agente_tool/docs/architecture.md` descrevendo novo fluxo com `ToolNode`, incluindo diagrama textual do roteamento (invoke → tools → handle → finalize).
- [ ] T231 [US3] Atualizar `agente_tool/docs/baseline.md` com execução pós-migração (“Depois da migração ToolNode”) destacando ausência de `partial`.
- [ ] T232 [US3] Registrar resumo da mudança e impacto em `PROJETOS.md` (seção referente ao agente_tool).

---

## Phase N: Polish & Verificação Final

- [ ] T240 [US2] Executar `ruff check agente_tool` garantindo ausência de novos lint warnings.
- [ ] T241 [US2] Garantir que `create_app` compila com e sem injeção de ferramentas (`python -m agente_tool.cli run`), arquivando notas em `specs/021-agente-tool-toolnode/research.md`.
- [ ] T242 [US3] Encerrar checklist atualizando este arquivo (`tasks.md`) com status das tarefas e registrar decisões pendentes na seção “Open Questions” de `plan.md`.

---

## Dependências e Paralelismo

- **Fases 1 e 2** dependem de conclusão da Fase 0.
- Fase 3 inicia somente após grafo atualizado (T210–T213).
- Documentação (Fase 4) pode começar após T213, rodando em paralelo com testes.
- Polishing (Fase N) somente após testes verdes e docs atualizados.

---

## Estratégia de Entrega

1. **Entrega 1**: Fases 0–2 (grafo rodando com `ToolNode`, testes temporariamente quebrados).
2. **Entrega 2**: Fase 3 (suíte de testes verde).
3. **Entrega 3**: Fase 4 + Polish (doc + lint + CLI).

Cada entrega deve atualizar `graph-nodes-patterns.md` e `agente_tool/docs/baseline.md` conforme aplicável, mantendo rastreabilidade no repositório.
