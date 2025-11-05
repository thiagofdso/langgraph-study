# Data Model: Refactor agente_imagem Structure

## 1. Entities

### 1.1 ImageAnalysisRequest
- **Fields**:
  - `image_path: str` – caminho do arquivo informado pelo usuário ou padrão `folder_map.png` (T6, T8).
  - `messages: list[BaseMessage]` – histórico opcional caso o agente seja acionado via LangGraph CLI (especificação, FR-001).
  - `metadata: dict` – informações auxiliares (timestamp de execução, nome do arquivo) herdadas do padrão `agente_simples`.
- **Validation Rules**:
  - Se o caminho estiver vazio usar fallback padrão (T6 `validate_input_node`).
  - Deve garantir existência do arquivo; se ausente, criar imagem dummy (T15).
- **Relationships**:
  - Alimenta diretamente o estado `GraphState` do workflow.

### 1.2 ImageAnalysisState (GraphState)
- **Fields** (TypedDict em `state.py`):
  - `messages: list[BaseMessage]` – acumulado com reducer `add_messages` (T4, T6).
  - `image_path: str` – caminho atual tratado por `validate_input_node` (T6).
  - `base64_image: str` – resultado da codificação em `prepare_image_node` (T6, T5).
  - `llm_response: str` – conteúdo retornado por Gemini (T6 `invoke_model_node`).
  - `markdown_output: str | None` – texto final entregue (T6 `format_response_node`).
  - `status: Literal["validated", "invoked", "formatted", "error"]` – evolução de estados (T4).
  - `error: str | None` – mensagem opcional para logs e testes de falha (T6, T13).
  - `duration_seconds: float | None` – métrica calculada durante formatação para manter paridade com `agente_simples` (especificação, Edge Cases).
- **Validation Rules**:
  - `status` deve seguir o conjunto controlado definido em `state.py` (T4).
  - `markdown_output` só é preenchido quando o conteúdo não contém `INVALID_IMAGE` (T6).
- **Relationships**:
  - Intermediário entre nodes; transições lineares `validate_input` → `prepare_image` → `invoke_model` → `format_response` (T7).

### 1.3 ImageAnalysisResult
- **Fields**:
  - `markdown_output: str | None` – resultado final exposto pela CLI e testes (FR-003, T8, T13).
  - `status: str` – indica sucesso ou erro para logs e mensagens (T6, T12).
  - `logs: list[str]` – produzidos via `utils/logging` (T12) e usados para validação manual.
- **Validation Rules**:
  - Em caso de erro deve preservar mensagens equivalentes às anteriores (spec Edge Cases).

## 2. State Transitions
1. **Initial**: estado bruto com `image_path` fornecido (ou ausente).
2. **Validated**: `validate_input_node` garante caminho e inicializa metadata (`status=validated`).
3. **Prepared**: `prepare_image_node` gera `base64_image`; se falhar, `status=error` e fluxo encerra.
4. **Invoked**: `invoke_model_node` popula `llm_response` e define `status=invoked`.
5. **Formatted**: `format_response_node` avalia resposta; sucesso → `status=formatted` com markdown, erro → `status=error`.

## 3. Derived Data & Side Effects
- Criação de imagem dummy via `ensure_sample_image` (T5, T15) assegura testes consistentes.
- Logs estruturados criados através de `get_logger` (T12) acompanham cada transição.
- CLI retorna apenas `markdown_output`, mantendo retrocompatibilidade com `main.py` original.
