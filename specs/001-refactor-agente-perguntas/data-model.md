# Data Model: Reestruturar Agente Perguntas

## Overview
A refatoração mantém os dados em memória, mas formaliza modelos conceituais para configuração, FAQ e estado de execução do agente. Cada entidade guiará tipagens (`TypedDict` ou `pydantic`) e validações no código refatorado.

## Entities

### AgentConfiguration
- **Purpose**: Agrupa variáveis de ambiente e parâmetros padrão usados pelo CLI e pelo grafo.
- **Fields**:
  - `gemini_api_key: str` — obrigatório; deve ser string não vazia.
  - `model_name: str` — padrão `gemini-2.5-flash`; aceita override via ENV.
  - `temperature: float` — padrão `0.2`; restringir ao intervalo `[0.0, 1.0]`.
  - `confidence_threshold: float` — padrão `0.7`; restringir ao intervalo `[0.0, 1.0]`.
  - `log_dir: pathlib.Path` — diretório para logs; criar automaticamente se não existir.
- **Validation Rules**:
  - Falha com mensagem orientativa se `gemini_api_key` estiver ausente.
  - Normalizar `temperature`/`confidence_threshold` para limites válidos.
- **Relationships**: Fornece parâmetros para `AgentState` e helpers de similaridade/logging.

### FAQEntry
- **Purpose**: Representa uma linha do FAQ utilizado para respostas automáticas.
- **Fields**:
  - `question: str`
  - `answer: str`
  - `tags: list[str]` — lista opcional de rótulos temáticos.
- **Validation Rules**:
  - Normalizar perguntas/respostas removendo espaços excedentes.
  - Tags devem ser strings não vazias.
- **Relationships**: Consumido pelos utilitários de prompt e similaridade; complementa `InteractionState` com notas.

### InteractionState
- **Purpose**: Estado do fluxo para cada pergunta processada.
- **Fields**:
  - `question: str`
  - `answer: str`
  - `confidence: float`
  - `status: Literal["respondido automaticamente", "encaminhar para humano"]`
  - `notes: str`
  - `messages: list[dict]` — histórico acumulado para compatibilidade futura com mensagens LangGraph (usando reducer `add_messages`).
- **Validation Rules**:
  - `confidence` limitado a `[0.0, 1.0]`.
  - `question` deve ser string não vazia (trimming antes do node).
  - `notes` obrigatório após escalonamento.
- **State Transitions**:
  - Inicial: apenas `question` preenchido.
  - Após avaliação automática: popula `answer`, `confidence`, `status="respondido automaticamente"`, `notes` descrevendo correspondência.
  - Após HITL: `status="encaminhar para humano"`, `answer` e `notes` refletindo input humano.

## Derived Collections
- **LogRecord** (conceitual): timestamp, pergunta, status final, duração; utilizado apenas para logging estruturado.

## Storage Considerations
- Não há persistência de FAQ além do módulo `utils/prompts.py`.
- Logs permanecem em disco local sob `config.log_dir`.
- Estado efêmero por execução; `thread_id` diferencia sessões quando necessário.
