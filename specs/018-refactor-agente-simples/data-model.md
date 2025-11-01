# Data Model: Refactor Simple Agent

## ConversationSession
- **Purpose**: Registrar cada execução do agente no CLI.
- **Fields**:
  - `question` (str, obrigatório): pergunta original do operador, validada com comprimento mínimo de 5 caracteres.
  - `answer` (str, opcional): resposta final formatada exibida ao usuário.
  - `status` (Literal[`pending`, `completed`, `error`]): estado de processamento do fluxo.
  - `timestamp` (datetime): momento da execução; default para `datetime.utcnow()` no logger/formatação.
  - `error_message` (str, opcional): mensagem amigável quando ocorre falha controlada.
  - `metadata` (dict, opcional): informações adicionais (ex.: idioma, duração).
- **Validation Rules**:
  - `question` deve ser normalizada (trim) antes de validação.
  - `status` deve acompanhar o ponto do grafo (pending → completed | error).
  - `answer` é obrigatória quando `status == "completed"`.
  - `error_message` é obrigatória quando `status == "error"`.
- **State Transitions**:
  1. `pending`: criação após leitura do CLI e validação da entrada.
  2. `completed`: sucesso na chamada ao modelo e formatação final.
  3. `error`: falha de validação ou exceção tratada no node de invocação.

## RuntimeConfigurationProfile
- **Purpose**: Concentra dependências e parâmetros de execução configuráveis.
- **Fields**:
  - `model_name` (str, default `"gemini-2.5-flash"`): modelo padrão definido pela Constituição.
  - `temperature` (float, default `0.0`): controla variação das respostas.
  - `timeout_seconds` (int, default `30`): limite para chamadas ao provedor.
  - `locale` (str, default `"pt-BR"`): idioma usado em mensagens e prompts.
  - `api_key` (str): carregada do `.env`; obrigatória na inicialização.
  - `checkpointer` (MemorySaver | outro): instância retornada dinamicamente.
- **Validation Rules**:
  - `api_key` não pode ser vazio; lançar exceção com orientação de configuração.
  - `temperature` deve estar no intervalo `[0.0, 1.0]`.
  - `timeout_seconds` deve ser positivo; valores <5s disparam warning.
  - Valores devem permitir override via variáveis de ambiente sem alterar código.
- **Relationships**:
  - `ConversationSession` referencia a configuração ativa para registrar `model_name` e `temperature` usados.

## LogEntry (derivado do logger)
- **Purpose**: Representar registros estruturados gravados em arquivo.
- **Fields**:
  - `timestamp` (datetime): carimbo do log.
  - `level` (Literal[`DEBUG`, `INFO`, `WARNING`, `ERROR`]): severidade.
  - `message` (str): descrição.
  - `context` (dict, opcional): metadados (question, status, duration).
- **Validation Rules**:
  - Logs de erro devem incluir `context["question"]` quando aplicável.
  - Níveis `INFO` e `ERROR` são mínimos para persistência em arquivo.
- **State Transitions**:
  - Todo `ConversationSession` deve gerar pelo menos um `INFO` de sucesso ou erro; `DEBUG` reservado para ambiente de desenvolvimento.
