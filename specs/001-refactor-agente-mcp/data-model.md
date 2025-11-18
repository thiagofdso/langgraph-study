# Data Model: Refatorar agente_mcp

## 1. AgentSession
- **Purpose**: Representa uma execução do agente do ponto de vista do usuário/QA manual.
- **Fields**:
  - `thread_id: str` — identificador passado ao LangGraph (default `manual-run`), obrigatório.
  - `messages: list[BaseMessage]` — histórico acumulado, gerenciado via reducer `add_messages`.
  - `run_log: list[dict]` — eventos estruturados por etapa (`phase`, `tool_name`, `status`, `duration_ms`).
  - `metadata: dict` — configuração derivada (LLM model, servers ativados, timestamp de início/fim).
  - `errors: list[dict]` — registros de falhas recuperáveis (categoria, mensagem amigável).
- **Relationships**: Mantém referência indireta aos `ServerProfile` carregados para saber quais ferramentas estão disponíveis.
- **Validation Rules**:
  - `thread_id` não pode ser vazio; aplicar `str.strip()` e fallback para `manual-run`.
  - `messages` precisa iniciar com `SystemMessage` padronizada + `HumanMessage` de entrada.
  - `run_log`/`errors` devem ser limitados para evitar explosão (p.ex. máximo 200 entradas).

## 2. ServerProfile
- **Purpose**: Define cada servidor MCP disponível para o MultiServerMCPClient.
- **Fields**:
  - `name: str` — identificador único (usado como namespace de ferramentas).
  - `transport: Literal["stdio", "sse"]` — meio de comunicação.
  - `endpoint: str` — comando (`python agente_mcp/mcp_servers/math_server.py`) ou URL.
  - `auto_start: bool` — indica se o `main.py` deve iniciar/encerrar o processo.
  - `env: dict[str, str]` — variáveis específicas (opcional).
  - `timeout_seconds: int` — limite para inicialização/resposta.
- **Relationships**: Coleção ordenada carregada por `load_server_profiles()`; usada para construir o `MultiServerMCPClient` e alimentar o README/quickstart.
- **Validation Rules**:
  - `name` deve ser único e seguir snake_case para evitar conflitos em `tool_calls`.
  - `transport` precisa ser suportado pelo cliente.
  - `endpoint` deve existir (arquivo ou URL) antes de iniciar a sessão, validado pelo config loader.

## 3. ExecutionConfig
- **Purpose**: Centraliza parâmetros de execução manual carregados do `.env` + defaults.
- **Fields**:
  - `gemini_api_key: str` — obrigatório; verificado no boot.
  - `default_questions: list[str]` — perguntas executadas automaticamente quando nenhuma entrada manual é fornecida.
  - `auto_start_servers: bool` — controla se `main.py` invoca `start_required_servers()`.
  - `log_level: Literal["INFO", "DEBUG", "ERROR"]` — determina verbosidade do logger estruturado.
  - `checkpointer_kind: Literal["memory", "sqlite"]` — para permitir troca futura sem mudar grafo.
- **Relationships**: Consumido por `main.py` → `config.py` → `graph.py`; referenciado pelo README/quickstart.
- **Validation Rules**:
  - `gemini_api_key` não pode estar vazio.
  - `default_questions` precisa conter pelo menos uma pergunta para garantir demonstração rápida (<10 minutos).
  - `checkpointer_kind` valida opções suportadas e seleciona implementações (MemorySaver como default).
