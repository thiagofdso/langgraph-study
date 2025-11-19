# Data Model: Graph-Managed Task Workflow

## 1. AgentState (root)
| Field | Type | Source | Description | Validation |
|-------|------|--------|-------------|------------|
| `messages` | `List[BaseMessage]` | LangGraph reducer (`add_messages`) | Conversa acumulada enviada/recebida pelo agente. | Sempre inicia com `SystemMessage`; `HumanMessage`/`AIMessage` adicionados em ordem cronológica. |
| `tasks` | `List[TaskItem]` | Nodes `prepare_round1`, `append_tasks` | Lista mutável de tarefas em memória. | IDs devem ser únicos; status pertence ao conjunto {`pending`, `completed`}. |
| `completed_ids` | `List[int]` | Node `complete_task` | IDs marcados como concluídos. | Cada ID deve existir em `tasks`; não pode repetir. |
| `timeline` | `List[TimelineEntry]` | Todos os nodes | Log sequencial das três rodadas. | Deve conter um registro por rodada executada em ordem (`round1`→`round2`→`round3`). |
| `duplicate_notes` | `List[str]` | Node `append_tasks` | Observações sobre duplicatas aceitas. | Opcional; só existe quando houver duplicatas confirmadas. |
| `round_payload` | `Dict[str, object]` | CLI → nodes | Envelope temporário com dados da rodada atual (entradas do usuário, decisões). | Resetado para `{}` após cada node processar sua rodada. |

## 2. TaskItem
| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| `id` | `int` | Identificador incremental atribuído na Rodada 1 ou 3. | Deve permanecer estável durante a sessão. |
| `description` | `str` | Texto curto da tarefa. | Proveniente do input do usuário, normalizado (`strip`). |
| `status` | `Literal["pending", "completed"]` | Estado atual. | Atualizado apenas por nodes. |
| `source_round` | `Literal["round1", "round3"]` | Rodada de origem. | Facilita auditoria e mensagens contextualizadas. |

## 3. TimelineEntry
| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| `round_id` | `Literal["round1","round2","round3"]` | Indica a etapa do fluxo. | Determina a ordem esperada na timeline. |
| `user_input` | `str` | Texto recebido do usuário (tarefas, ID, resumo). | Pode armazenar número ou "Nenhuma tarefa adicionada". |
| `agent_response` | `str` | Última resposta do agente gerada no node correspondente. | Exibida pelo CLI e LangGraph CLI. |
| `notes` | `Optional[str]` | Informações adicionais (duplicatas, confirmações). | Populado principalmente no node de Rodada 3. |

## 4. Node Payload Helpers
| Payload | Fields | Purpose |
|---------|--------|---------|
| `Round1Payload` | `initial_tasks: List[str]`, `prompt_messages: List[BaseMessage]` | Permite ao CLI enviar apenas entradas do usuário para o node `prepare_round1`. |
| `Round2Payload` | `selected_id: int`, `prompt_messages: List[BaseMessage]` | Usado por `complete_task` para validar e responder. |
| `Round3Payload` | `new_tasks: List[str]`, `duplicate_decisions: List[str]`, `prompt_messages: List[BaseMessage]` | Fornece contexto ao node `append_tasks`. |

## 5. Relationships & Transitions
- `AgentState.tasks` e `AgentState.completed_ids` são sincronizados: sempre que um ID entra em `completed_ids`, o `TaskItem.status` correspondente vira `completed`.
- `TimelineEntry` referencia indiretamente `TaskItem` via `round_id` e `notes`; não há foreign key explícito, apenas consistência posicional.
- Nodes atualizam o estado em sequência; cada node deve retornar o estado completo para garantir que checkpointer consiga retomar a mesma transição.

## 6. Validation Rules Summary
1. A execução deve seguir a ordem fixa (round1 → round2 → round3). Qualquer payload fora de ordem deve resultar em erro amigável.
2. IDs das tarefas são inteiros positivos atribuídos sequencialmente; Rodada 3 deve continuar incrementando a partir do maior `id` existente.
3. Mensagens retornadas pelos nodes precisam incluir pelo menos um `AIMessage` com conteúdo textual para o CLI exibir.
4. Timeline precisa registrar exatamente uma entrada por rodada efetivamente concluída, garantindo auditoria e sucesso do critério SC-004.
