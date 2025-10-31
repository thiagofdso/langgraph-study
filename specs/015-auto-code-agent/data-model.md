# Data Model – Simplified Code Generation Loop

## Entities

### AgentState
- **Description**: Estrutura mantida pelo LangGraph para cada execução do agente.
- **Fields**:
  - `messages` (list[BaseMessage]): Histórico de mensagens utilizados pelos nós que chamam o LLM.
  - `iteration_count` (int): Contador iniciado em 0 e incrementado pelo nó de geração antes de invocar o modelo.
  - `code` (str | None): Código Python mais recente produzido e compartilhado entre os nós.
  - `execution_result` (ExecutionResult | None): Resultado da última execução, incluído apenas após o nó de execução rodar.
  - `reflection_feedback` (str | None): Texto retornado pelo nó de reflexão, usado como insumo adicional para a próxima geração.
  - `status` (Literal[`"running"`, `"success"`, `"limit_reached"`, `"error"`]): Estado do loop, atualizado pelo nó de decisão.
- **Validation Rules**:
  - `iteration_count` deve permanecer ≤ `MAX_ITERATIONS`.
  - `code` deve ser string não vazia quando `status` for `"success"` ou `"error"`.
  - `reflection_feedback` é preenchido apenas quando houve erro na execução.

### ExecutionResult
- **Description**: Pacote com dados retornados pela avaliação em memória do código.
- **Fields**:
  - `stdout` (str): Saída padrão capturada durante `exec`.
  - `stderr` (str): Mensagens de erro ou avisos relevantes.
  - `exception` (str | None): Traceback textual quando ocorre falha.
  - `return_code` (int): `0` para sucesso, `1` para falha controlada; outros valores reservados para exceções inesperadas.
- **Validation Rules**:
  - `return_code == 0` implica `exception is None`.
  - `return_code != 0` deve carregar ao menos `stderr` ou `exception`.

### LoopSummary
- **Description**: Visão consolidada usada apenas para impressão final no console.
- **Fields**:
  - `total_iterations` (int): Quantidade de ciclos executados.
  - `final_status` (Literal[`"success"`, `"limit_reached"`, `"error"`]): Resultado comunicado ao usuário.
  - `final_code` (str | None): Código apresentado quando `final_status == "success"`.
- **Validation Rules**:
  - `total_iterations` corresponde ao valor final de `iteration_count`.
  - `final_code` deve ser não nulo quando `final_status == "success"`.
- **Relationships**:
  - Construído a partir de `AgentState` ao encerrar o grafo; não é persistido entre execuções.
