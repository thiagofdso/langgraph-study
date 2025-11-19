# Research: Graph-Managed Task Workflow

## Decision 1: Use dedicated LangGraph nodes (prepare → complete → append → summarize)
- **Rationale**: `langgraph-tasks.md` highlights the need to encapsulate cada rodada em nodes próprios para permitir retomada via checkpointer e compatibilidade com LangGraph CLI. Projetos similares listados em `PROJETOS.md` (como `agente_memoria` e `agente_imagem`) mostram que dividir responsabilidades por etapa simplifica testes e mantém o CLI fino. Reusar o padrão sequencial do `graph-nodes-patterns.md` evita divergência de nomenclatura.
- **Alternatives Considered**:
  1. Manter um único node e mover toda a lógica de estado para helpers chamados pelo CLI — rejeitado porque não atenderia ao requisito de atualizar estado dentro do grafo.
  2. Migrar para Functional API (`@entrypoint` + `@task`) — rejeitado porque o projeto precisa continuar exposto via `langgraph run agente-tarefas` e já utiliza `StateGraph` em outros agentes.

## Decision 2: Persist state fields exactly as definidos em `AgentState` com reducers mínimos
- **Rationale**: O spec pede que `tasks`, `completed_ids` e `timeline` vivam no grafo. Mantendo-os como listas simples, com `add_messages` apenas para mensagens, simplificamos a compatibilidade com checkpointer e com testes existentes. Novos metadados (ex.: `duplicate_notes`) serão adicionados apenas se realmente necessários, seguindo YAGNI e evitando inflar o estado.
- **Alternatives Considered**:
  1. Introduzir dataclasses/pydantic models para cada rodada — rejeitado por aumentar validações sem benefício claro e por divergir dos demais agentes.
  2. Guardar decisões temporárias no CLI e apenas sincronizar no final — inviável porque o LangGraph CLI precisa executar sem o CLI customizado.

## Decision 3: Cobrir o fluxo com testes unitários de nodes + integração do grafo e validar manualmente LangGraph CLI
- **Rationale**: O spec exige que `pytest`, `python -m agente_tarefas` e LangGraph CLI continuem funcionando. Planejamos criar `tests/test_nodes.py` para validar cada node determinístico e atualizar `test_graph.py`/`test_cli.py` para o fluxo completo. Testes diretos do `langgraph run` serão documentados e executados manualmente, conforme requisito explícito do usuário.
- **Alternatives Considered**:
  1. Simular LangGraph CLI em pytest — rejeitado porque seria frágil e o usuário já sinalizou que fará testes manuais dessa interface.
  2. Manter apenas testes de CLI — rejeitado porque não verificaria que o grafo sozinho mantém estado correto.

All clarifications resolved during research; no additional open questions remain for planning.

## Current CLI Mutation Points (T001)
- **`_round_one` (`agente_tarefas/cli.py:64-77`)**: limpa `tasks_state` e o repopula com `build_initial_tasks`; também registra timeline depois que o grafo responde usando `append_entry`.
- **`_round_two` (`cli.py:81-94`)**: delega a `select_completed_task`, que altera `tasks_state` marcando `status="completed"` e adiciona o ID em `completed_ids` (ver `utils/rounds.py:32-57`).
- **`_round_three` (`cli.py:95-126`)**: chama `collect_new_tasks` para anexar novas entradas a `tasks_state` e gravar notas de duplicidade; timeline é atualizada manualmente no CLI após a resposta do grafo.
- **Timeline appends (`cli.py:160-208`)**: cada rodada chama `append_entry` diretamente para inserir registros no `timeline` local, antes de repassar o estado ao grafo.
- **`collect_new_tasks` (`utils/rounds.py:59-104`)**: manipula `tasks_state` e `duplicate_notes` enquanto confirma duplicatas junto ao usuário, além de atualizar IDs incrementais.

Esses pontos precisam migrar para nodes dedicados para que o CLI não toque mais em `tasks`, `completed_ids` e `timeline` diretamente.
