# Data Model – Refatorar agente_tool

## GraphState
- **Purpose**: Representa o estado compartilhado entre os nodes do LangGraph.
- **Fields**:
  - `messages: list[BaseMessage]` – histórico de mensagens; reduzido com `add_messages`.
  - `metadata: dict[str, Any]` – dados auxiliares (ex.: pergunta original, prompt do sistema, tempo de início).
  - `status: str` – estado corrente do fluxo (`validated`, `responded`, `completed`, `error`).
  - `resposta: str` – texto final exibido ao usuário.
  - `selected_tool: str` – nome da ferramenta planejada (quando houver).
  - `tool_call: dict[str, Any]` – argumentos usados na última chamada de ferramenta.
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
- **Validation Rules**:
  - `name` deve corresponder a ferramenta registrada.
  - `args` só é propagado após validação de segurança (ex.: expressão matemática válida).
