# Documento de Tarefa: Graph-Managed Task Workflow

## 1. Análise Atual

### 1.1 Estado Atual
- **Project Structure**: `agente_tarefas/` segue a estrutura básica (config, graph, state, cli, utils, tests). O grafo atual (`graph.py`) contém apenas um node "agent" que invoca o LLM; toda a lógica de atualização das listas de tarefas ocorre localmente no CLI.
- **State Schema**: `AgentState` (TypedDict) com `messages`, `tasks`, `completed_ids`, `timeline`. Reducers só existem para `messages`; timelines e tarefas são manipuladas pelo CLI, o que impede reuso em LangGraph CLI.
- **Nodes/Tasks**: `utils/nodes.py` exporta somente `build_agent_node`. Não há nodes específicos para ingestão, conclusão ou acréscimo de tarefas.
- **Testes**: `tests/test_cli.py` cobre o fluxo feliz do CLI com um modelo fake; `tests/test_graph.py` apenas garante que o grafo compila. Não existem testes que invoquem o grafo diretamente para validar que `tasks`/`completed_ids` são atualizados pelos nodes.

### 1.2 Impacto da Mudança
- Componentes afetados: `graph.py`, `cli.py`, `state.py`, `utils/nodes.py`, `utils/rounds.py` (possível refactor de helpers), `tests/` e docs.
- Riscos: regressões na experiência principal (`python -m agente_tarefas`), incompatibilidade com `langgraph run agente-tarefas`, atrasos nos prompts se os nodes não preservarem o contexto, e inconsistência de estado ao retomar threads do checkpointer.

## 2. Requisitos & Objetivos

### 2.1 Objetivo Principal
Mover toda a lógica de atualização do estado para nodes do grafo, permitindo que tanto o CLI tradicional quanto o LangGraph CLI (execuções manuais) compartilhem o mesmo fluxo e garantindo que testes automatizados (pytest e `python -m agente_tarefas`) continuem funcionando.

### 2.2 Escolha de API
- **Graph API (StateGraph)** continuará sendo usada, agora com múltiplos nodes sequenciais/condicionais para cada rodada. Essa decisão facilita visualização no LangGraph Studio e mantém compatibilidade com `langgraph run`.

### 2.3 Estrutura de Projeto
- Permanece a estrutura básica existente. Os nodes podem ficar em `utils/nodes.py` (com funções auxiliares separadas) ou em submódulos se necessário, mantendo `graph.py` enxuto.

## 3. Organização de Arquivos

### 3.1 Estrutura Base
```
agente_tarefas/
├── graph.py          # Atualizar com novos nodes e edges
├── cli.py            # Reduzido a coletar input e invocar nodes
├── state.py          # Pode ganhar helpers/validadores adicionais
├── utils/
│   ├── nodes.py      # Definir nodes para cada rodada + helper de resposta
│   ├── prompts.py    # Já contém builders; reutilizar dentro dos nodes
│   ├── rounds.py     # Funções de parsing/validação reaproveitadas pelos nodes
│   └── timeline.py   # Continue sendo usado, agora chamado por nodes
└── tests/
    ├── test_nodes.py (novo)
    ├── test_graph.py (atualizado)
    └── test_cli.py   (ajustado)
```

### 3.2 Padrões de Importação
- Seguir convenção `stdlib -> third-party -> local`.
- Evitar importes circulares isolando builders de prompt/rounds em módulos específicos.

## 4. Implementação Detalhada

### 4.1 State & Config
1. **`state.py`**
   - Revisar `AgentState` para garantir que reducers adequados estejam configurados (`add_messages` já aplicado). Avaliar se `duplicate_notes` precisa entrar no estado global; se sim, adicionar novo campo com reducer apropriado.
   - Expandir `StateFactory` com métodos auxiliares (ex.: `build_empty()` ou `with_tasks(tasks)`) para simplificar os testes dos nodes.

2. **`config.py`**
   - Nenhuma alteração estrutural, apenas garantir que `create_llm` e `create_checkpointer` continuam acessíveis para injeção nos nodes.

### 4.2 Nodes / Fluxo do Grafo
Criar nodes especializados para encapsular cada etapa. Nome sugerido e responsabilidades:

1. **`prepare_round1`**
   - Input: mensagens iniciais + payload da Rodada 1.
   - Responsabilidades: usar `build_round1_prompt` para gerar prompt, copiar tarefas parseadas pelo CLI para o estado, chamar LLM e registrar timeline.

2. **`complete_task_node`**
   - Input: ID selecionado na Rodada 2.
   - Responsabilidades: validar ID via `select_completed_task`, atualizar `tasks` e `completed_ids`, construir prompt com `build_round2_prompt`, chamar LLM e atualizar timeline.

3. **`append_tasks_node`**
   - Input: lista de novas tarefas + notas de duplicidade.
   - Responsabilidades: reutilizar `collect_new_tasks`, atualizar `tasks`, anexar notas, chamar LLM com `build_round3_prompt`, registrar timeline.

4. **`emit_summary_node`** (opcional se o node anterior já retorna saída final)
   - Garante que qualquer lógica adicional (ex.: resumo geral, insight final) aconteça dentro do grafo.

5. **Edge Logic**
   - `START -> prepare_round1 -> complete_task_node -> append_tasks_node -> END`.
   - Cada node deve retornar estado completo para permitir reexecução ou retomada via checkpointer.

### 4.3 Ajustes no CLI
1. **Isolar o CLI como orquestrador**
   - Após coletar cada entrada do usuário, montar um pacote (`payload`) que será enviado ao grafo (por exemplo, mensagens + metadados da rodada) sem alterar `tasks` localmente.
   - Consumir o retorno do grafo para exibir respostas e atualizar a exibição local, mas sem mutar o estado compartilhado.

2. **Threading e Config**
   - Continuar usando `thread_id` via `settings.build_thread_id()` para garantir que LangGraph CLI e CLI manual compartilhem semântica de sessão.

### 4.4 Ajustes no Grafo / LangGraph CLI
1. **`graph.py`**
   - Definir builder `workflow = StateGraph(AgentState)`.
   - Registrar nodes criados na seção 4.2.
   - Configurar entradas/saídas para que LangGraph CLI (executado manualmente) aceite payload com `messages` e campos auxiliares (por exemplo, `control.round` para indicar o node a executar, se necessário).

2. **`langgraph.json`**
   - Confirmar que continua apontando para `agente_tarefas/graph.py:create_graph`.

### 4.5 Atualizações de Documentação
- `README.md` ou `docs/operations.md`: adicionar breve nota explicando que o estado agora é gerenciado pelos nodes e como testar via LangGraph CLI.

## 5. Plano de Testes

### 5.1 Testes Automatizados (pytest)
1. **Novos testes de nodes (`tests/test_nodes.py`)**
   - Cobrir cada node individual usando estados sintéticos (ex.: rodadas fora de ordem devem falhar; duplicatas devem gerar notas).
2. **`tests/test_graph.py`**
   - Atualizar para invocar o grafo com sequências completas e verificar que `tasks`, `completed_ids` e `timeline` foram atualizados exclusivamente pelos nodes.
3. **`tests/test_cli.py`**
   - Ajustar mocks para confirmar que o CLI não altera o estado localmente e apenas encaminha payloads ao grafo.

### 5.2 Testes via `python -m agente_tarefas`
- Executar smoke test interativo confirmando que o CLI imprime respostas coerentes e que as listas exibidas refletem o estado retornado pelo grafo.

### 5.3 Testes LangGraph CLI (manuais)
- Documentar no PR/README os passos para rodar `langgraph run agente-tarefas --input ...` e verificar que o estado final contém tarefas adicionadas/concluídas.

## 6. Deploy & Monitoramento
- Confirmar que `langgraph run` e LangGraph Studio conseguem visualizar o fluxo com múltiplos nodes.
- Verificar logs/timelines para garantir rastreabilidade.

## 7. Backlog de Tarefas Detalhadas

| # | Tarefa | Arquivos / Artefatos | Critérios de Aceite |
|---|--------|----------------------|---------------------|
| 1 | Mapear dependências atuais do CLI sobre estado local e documentar pontos de mutação. | `agente_tarefas/cli.py`, `utils/rounds.py` | Lista clara de locais onde `tasks`, `completed_ids` e `timeline` são alterados diretamente. |
| 2 | Atualizar `state.py` com helpers/reducers necessários (ex.: campo `duplicate_notes` se persistir no estado). | `agente_tarefas/state.py` | Estado inicial pode ser instanciado sem CLI; reducers evitam perda de dados em reexecuções. |
| 3 | Implementar node `prepare_round1` que recebe tarefas parseadas e grava timeline dentro do grafo. | `utils/nodes.py`, `utils/prompts.py` | Node retorna `tasks` preenchidos e mensagem do agente; testes de unidade confirmam persistência. |
| 4 | Implementar node `complete_task_node` para Rodada 2, validando IDs e atualizando `completed_ids`. | `utils/nodes.py`, `utils/rounds.py` | Testes garantem falha amigável quando ID inválido ou repetido. |
| 5 | Implementar node `append_tasks_node` para Rodada 3, incluindo registro de duplicatas e resumo final. | `utils/nodes.py`, `utils/rounds.py`, `utils/timeline.py` | Node adiciona novas tarefas e escreve notas de duplicidade na timeline. |
| 6 | Revisar `graph.py` para construir o fluxo sequencial/condicional com os novos nodes e checkpointer configurado. | `agente_tarefas/graph.py` | Grafo compila; LangGraph CLI consegue percorrer todos os nodes sem dependências do CLI. |
| 7 | Atualizar `cli.py` para remover mutações diretas de estado e enviar/receber dados exclusivamente via grafo. | `agente_tarefas/cli.py` | CLI usa apenas o estado retornado pelo grafo; testes comprovam que listas locais não divergem. |
| 8 | Acrescentar testes unitários de nodes e atualizar `test_graph.py`/`test_cli.py` para refletir o novo fluxo. | `agente_tarefas/tests/` | `pytest agente_tarefas/tests -q` passa; novos testes validam mutações feitas pelos nodes. |
| 9 | Documentar instruções de execução via LangGraph CLI e main module (smoke test manual). | `agente_tarefas/docs/operations.md` ou `README.md` | Passos para `langgraph run agente-tarefas` listados; instruções sobre testes manuais registradas. |

## 8. Critérios de Pronto
- Todos os nodes exigidos estão implementados e cobertos por testes unitários.
- `graph.py` expõe fluxo completo sem reliance no CLI.
- CLI tradicional funciona ponta a ponta (teste manual verificado).
- `pytest agente_tarefas/tests -q` passa com novos testes que confirmam atualizações de estado dentro do grafo.
- LangGraph CLI é capaz de executar o fluxo (validado manualmente conforme solicitado).
- Documentação atualizada descrevendo novo comportamento e passos de teste.
