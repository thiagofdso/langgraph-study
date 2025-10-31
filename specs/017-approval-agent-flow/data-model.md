# Data Model — Agente com Aprovação Humana

## Overview
O agente mantém todo o estado em memória durante uma única execução. A estrutura abaixo garante rastreabilidade das validações, decisões humanas e resultados de busca antes da resposta final.

## Entities

### ApprovalSessionState
- **Description**: Estado agregado que o LangGraph manipula a cada nó.
- **Fields**
  - `question` (str) — Solicitação original do usuário.
  - `validated_input` (`ValidatedSubmission` | None) — Dados após validação.
  - `validation_errors` (List[str]) — Mensagens quando a entrada falha.
  - `validation_attempts` (int) — Número de tentativas realizadas.
  - `approval_required` (bool) — Indica se a próxima etapa precisa de aprovação.
  - `approval_decision` (`ApprovalOutcome` | None) — Resultado da última aprovação humana.
  - `search_results` (List[`SearchHit`]) — Respostas da ferramenta externa.
  - `response_text` (str) — Texto produzido pelo nó `gerar_resposta`.
  - `response_stage` (Literal["initial","final"]) — Fase atual da geração (define condicional).
  - `notes` (List[str]) — Avisos ao operador/usuário (ex.: “resposta sem pesquisa autorizada”).

### ValidatedSubmission
- **Description**: Representa a entrada pronta para aprovação.
- **Fields**
  - `prompt` (str) — Versão normalizada da pergunta.
  - `metadata` (dict[str, str]) — Campos opcionais coletados na validação (ex.: canal, prioridade).

### ApprovalOutcome
- **Description**: Registro da decisão humana devolvida via `interrupt`.
- **Fields**
  - `approved` (bool) — Indica se a ferramenta pode ser executada.
  - `reason` (str) — Justificativa textual do aprovador.
  - `timestamp` (datetime) — Momento da decisão.

### SearchHit
- **Description**: Entrada retornada pela ferramenta Tavily importada de `agente_web`.
- **Fields**
  - `title` (str) — Título da fonte.
  - `url` (str) — Link para consulta.
  - `snippet` (str) — Resumo ou conteúdo essencial.

### FinalResponse
- **Description**: Entrega final exibida ao usuário após fluxo completo.
- **Fields**
  - `text` (str) — Mensagem final consolidada.
  - `used_tool` (bool) — Indica se a pesquisa foi utilizada.
  - `human_notes` (str | None) — Comentários do aprovador incorporados.

## Relationships and Notes
- `ApprovalSessionState.response_stage` inicia em `"initial"`; ao alcançar `"final"` o grafo encerra (condicional no nó `gerar_resposta`).
- `validation_attempts` e `validation_errors` controlam a volta ao nó inicial quando a validação falha; limites serão aplicados nos requisitos funcionais.
- `ApprovalOutcome.approved = False` aciona rota alternativa que pula a busca e acrescenta aviso em `notes`.
- Todos os objetos vivem apenas durante a execução; `InMemorySaver` garante retomada após interrupções para aprovação humana sem persistência em disco.
