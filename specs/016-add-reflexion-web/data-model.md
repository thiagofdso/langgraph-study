# Data Model — Reflexion Web Evidence Agent

## Overview
O agente mantém todo o estado em memória durante a execução. Os objetos abaixo descrevem como o fluxo organiza a pergunta, as evidências externas, as iterações de rascunho/reflexão e a resposta final.

## Entities

### ReflectionSession
- **Description**: Representa uma execução completa do agente para a pergunta fixa.
- **Fields**
  - `question` (str) — Pergunta tratada no ciclo (sempre “Como funciona o Google Agent Development Kit?”).
  - `iterations` (List[`IterationRecord`]) — Histórico ordenado de rascunho/reflexão por ciclo.
  - `final_answer` (`FinalAnswer` | None) — Resultado consolidado com citações.
  - `warnings` (List[str]) — Avisos emitidos ao longo da execução (ex.: ausência de evidências).
  - `metadata` (dict) — Informações auxiliares (timestamps, duração total).

### IterationRecord
- **Description**: Captura um ciclo completo de geração + reflexão.
- **Fields**
  - `draft` (`DraftAnswer`) — Rascunho produzido antes da reflexão.
  - `reflection` (`ReflectionNote`) — Avaliação/crítica ligada ao rascunho.
  - `applied_corrections` (List[str]) — Mudanças planejadas para próxima iteração.
  - `used_evidence_ids` (List[str]) — Identificadores das evidências consultadas no ciclo.
  - `index` (int) — Ordem da iteração (1 a 3).

### Evidence
- **Description**: Fonte externa obtida via Tavily e normalizada para citações.
- **Fields**
  - `id` (str) — Identificador único (ex.: `ref-1`).
  - `title` (str) — Título da página retornada.
  - `url` (str) — Link direto para consulta.
  - `summary` (str) — Trecho relevante ou resumo usado no agente.
  - `source_name` (str) — Nome amigável do site/publicação.
  - `retrieved_at` (datetime) — Timestamp do momento da busca.

### DraftAnswer
- **Description**: Texto provisório gerado pelo nó de produção.
- **Fields**
  - `content` (str) — Texto completo do rascunho.
  - `citation_placeholders` (List[`CitationRef`]) — Marcação de onde inserir citações.

### ReflectionNote
- **Description**: Feedback estruturado baseado em evidências.
- **Fields**
  - `content` (str) — Texto da crítica (bullets de melhorias e riscos).
  - `referenced_evidence` (List[`EvidenceReference`]) — Vinculação explícita a fontes.

### EvidenceReference
- **Description**: Associação entre uma crítica/trecho do rascunho e uma evidência externa.
- **Fields**
  - `evidence_id` (str) — Identificador da evidência.
  - `reason` (str) — Justificativa do uso da evidência (ex.: “Confirma disponibilidade de Agentspace”).

### CitationRef
- **Description**: Estrutura auxiliar para compor citações numeradas no texto final.
- **Fields**
  - `evidence_id` (str) — Identificador da evidência associada.
  - `position` (int) — Ordem no texto em que a citação deve aparecer.

### FinalAnswer
- **Description**: Resposta final preparada para o usuário.
- **Fields**
  - `content` (str) — Texto final com citações formatadas.
  - `citations` (List[`CitationEntry`]) — Lista numerada com identificação da fonte.

### CitationEntry
- **Description**: Item formatado para a seção de referências.
- **Fields**
  - `label` (str) — Etiqueta numérica (ex.: “[1]”).
  - `title` (str) — Título da fonte exibido ao usuário.
  - `url` (str) — Link público para verificação.
  - `source_name` (str) — Nome do site/autor.
  - `retrieved_at` (datetime) — Data/Hora de coleta.

## Relationships and Notes
- Cada `ReflectionSession` possui até três `IterationRecord`.
- `IterationRecord.used_evidence_ids` deve refletir subconjunto dos IDs presentes em `ReflectionSession.evidences`.
- `FinalAnswer.citations` é derivado de `Evidence` e `CitationRef`; manter ordem consistente garante transparência.
- `InMemorySaver` preserva o estado entre nós do LangGraph; nenhuma entidade é persistida após a execução.
