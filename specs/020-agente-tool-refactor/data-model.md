# Data Model – Refatorar agente_tool

## GraphState
- **Purpose**: Representa o estado compartilhado entre os nodes do LangGraph.
- **Fields**:
  - `messages: list[BaseMessage]` – histórico de mensagens; reduzido com `add_messages`.
  - `metadata: dict[str, Any]` – dados auxiliares (ex.: pergunta original, prompt do sistema, tempo de início).
  - `status: str` – estado corrente do fluxo (`validated`, `responded`, `completed`, `error`).
  - `resposta: str` – texto final exibido ao usuário.
  - `selected_tools: list[str]` – nomes de todas as ferramentas solicitadas pelo modelo na rodada atual.
  - `tool_plans: list[ToolPlan]` – planos de execução pendentes para cada tool call.
  - `tool_calls: list[dict[str, Any]]` – resultados (ou erros) retornados pela execução das ferramentas.
  - `duration_seconds: float` – tempo total de execução (opcional, calculado no final).
- **Validation Rules**:
  - `messages` deve conter ao menos a mensagem do usuário antes da validação.
  - `status` usa conjunto controlado de valores para facilitar assertions em testes.

## ThreadConfig
- **Purpose**: Configuração por execução, garantindo identificador válido para checkpointer.
- **Fields**:
  - `thread_id: str` – ID alfanumérico (3–64 caracteres, regex `^[a-zA-Z0-9-_]+$`).
- **Validation Rules**:
  - Obrigatório; falhas interrompem a criação do grafo.

## ToolPlan
- **Purpose**: Estrutura intermediária para planejar uso da ferramenta calculadora.
- **Fields**:
  - `name: str` – nome da ferramenta (ex.: `"calculator"`).
  - `args: dict[str, Any]` – argumentos originais solicitados pelo modelo.
  - `call_id: str | None` – identificador emitido pelo modelo para correlacionar chamadas e respostas.
- **Validation Rules**:
  - `name` deve corresponder a ferramenta registrada.
  - `args` só é propagado após validação de segurança (ex.: expressão matemática válida).
