# Data Model: agente_memoria Refactor

## Entities

### ConversationThread
- **Description**: Identifica um contexto de conversa associado a um operador.
- **Fields**:
  - `thread_id` *(str, required, min_length=3, slug format)* — identificador informado pelo usuário ou gerado automaticamente.
  - `created_at` *(datetime, auto)* — marca a primeira execução do thread.
  - `updated_at` *(datetime, auto)* — atualizado a cada nova interação.
  - `status` *(Literal["active", "reset", "archived"])* — indica se o histórico está em uso ou foi reiniciado.
  - `metadata` *(dict, optional)* — armazena origem do comando e versão do agente.
- **Relationships**: 1:N com `RegisteredInteraction`.

### RegisteredInteraction
- **Description**: Representa mensagens individuais (usuário ou agente) persistidas no histórico.
- **Fields**:
  - `sequence` *(int, auto)* — ordem cronológica dentro do thread.
  - `role` *(Literal["user", "assistant", "system"])* — emissor da mensagem.
  - `content` *(str, required)* — texto normalizado armazenado.
  - `timestamp` *(datetime, auto)* — horário de registro.
  - `duration_seconds` *(float, optional, >=0)* — tempo gasto para gerar a resposta (mensagens do agente).
  - `error_category` *(Optional[str])* — preenchido quando a interação terminou com erro controlado.
- **Relationships**: N:1 com `ConversationThread`.

### RuntimeConfiguration
- **Description**: Agrega valores necessários para executar o agente com segurança.
- **Fields**:
  - `model_name` *(str, default="gemini-2.5-flash")* — deve permanecer consistente com a Constituição.
  - `temperature` *(float, 0.0–1.0)* — ajustável via `.env`.
  - `api_key` *(str, required)* — bloqueia execução se ausente.
  - `timeout_seconds` *(int, default=30, >=5)* — usado em chamadas ao LLM.
  - `default_thread_id` *(str, optional)* — thread usado quando operador não informa valor.
  - `log_dir` *(path, default `agente_memoria/logs`)* — pasta onde logs são armazenados.
- **Relationships**: Fornece dependências para nodes de validação, invocação e logging.

## State Schema

```python
class GraphState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    metadata: Dict[str, Any]
    status: str
    resposta: str
    thread_id: str
    duration_seconds: float
    error: str
```

- `messages` usa `add_messages` para acumular histórico sem mutação manual.
- `metadata` inclui `question`, `started_at`, `command`, `should_reset`.
- `status` transita entre `pending` → `validated` → `invoked` → `completed` ou `error`.
- `thread_id` garante roteamento correto no checkpointer.
- `error` armazena mensagem amigável em caso de falhas.

## State Transitions

1. **validate_input**: Recebe pergunta, aplica Pydantic e define `status=validated`.
2. **load_history**: Recupera histórico previamente salvo (se existir) e atualiza `messages` sem sobrescrever entrada atual.
3. **invoke_model**: Invoca Gemini com prompt contextualizado; sucesso define `status=responded`, erro define `status=error` e popula `error`.
4. **update_memory**: Acrescenta resposta nas mensagens, garante limpeza quando comando de reset for detectado.
5. **format_response**: Calcula `duration_seconds`, produz `resposta` final, ajusta `status` para `completed` ou mantém `error`.

## Validation Rules

- Perguntas precisam de ao menos 5 caracteres após trim; comandos especiais começam com `/`.
- `thread_id` deve permitir somente `[a-zA-Z0-9-_]` e ter entre 3 e 64 caracteres.
- Comando `/reset` limpa histórico e marca `status="reset"` em `ConversationThread`.
- Falhas de configuração bloqueiam execução antes de qualquer chamada ao LLM.

## Derived Data

- `duration_seconds` calculado em `format_response`.
- Logs armazenam `(thread_id, question, status, duration)` para auditoria.

## Persistence Notes

- InMemorySaver mantém histórico por `thread_id` durante o processo.
- Documentar caminho para alternar para armazenamento persistente (ex.: SQLite) reutilizando abstrações definidas em `config.py`.
