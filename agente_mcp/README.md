# Agente MCP

Agente multi-servidor escrito com LangGraph. O fluxo valida a configuração, descobre ferramentas expostas pelos servidores MCP (math + weather por padrão), executa as perguntas configuradas e imprime o histórico completo com `run_log` estruturado.

## Estrutura

```
agente_mcp/
├── __init__.py
├── __main__.py            # permite `python -m agente_mcp`
├── main.py                # CLI stand-alone
├── config.py              # AppConfig + carregamento de .env
├── state.py               # AgentSession + reducers
├── graph.py               # montagem do StateGraph
├── utils/                 # logging, nodes e perfis de servidores
├── docs/                  # README + guias específicos
└── mcp_servers/           # implementações FastMCP (math/weather)
```

## Pré-requisitos

1. **Ambiente Python**  
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Credenciais**  
   Copie `agente_mcp/.env.example` para `agente_mcp/.env` e informe:
   ```
   GEMINI_API_KEY="sua-chave-gemini"
   MCP_DEFAULT_QUESTIONS='["quanto é 150 vezes 3?", "qual o clima em Nova York?"]'
   ```
   Variáveis adicionais suportadas:
   - `MCP_AUTO_START_SERVERS` (default `true`)
   - `MCP_LOG_LEVEL`
   - `MCP_THREAD_ID` (prefixo usado quando nenhum ID explícito é passado)

## Executando os servidores MCP

- **Math (stdio)** é iniciado automaticamente pelo próprio agente (usa o interpretador atual).
- **Weather (SSE)** precisa estar escutando em `http://localhost:8000/sse`. Execute em outro terminal:
  ```bash
  source venv/bin/activate
  python agente_mcp/mcp_servers/weather_server.py
  ```
  Deixe rodando enquanto o agente estiver ativo.

## Rodando o agente

### CLI local
```
source venv/bin/activate
python -m agente_mcp                # usa MCP_THREAD_ID + índice
python -m agente_mcp suporte-qa     # força um thread_id específico
```

O script executa todas as perguntas definidas em `MCP_DEFAULT_QUESTIONS`, imprime `User:`/`Assistant:` e, ao final de cada pergunta, exibe o `run_log` com duração de cada tool-call. Logs estruturados adicionais são gravados em `agente_mcp/logs/`.

### LangGraph CLI / Studio

`langgraph.json` já contém a entrada `agente-mcp`. Para testar via HTTP:
1. Exporte as variáveis de ambiente (especialmente `GEMINI_API_KEY`).
2. Rode `langgraph dev`.
3. Utilize a interface para enviar mensagens. O `thread_id` informado na UI é preservado automaticamente.

## Adicionando servidores MCP

1. Crie o servidor em `agente_mcp/mcp_servers/<nome>_server.py` (FastMCP).
2. Adicione um `ServerProfile` em `agente_mcp/utils/servers.py` especificando `name`, `transport`, `endpoint`, `auto_start` e variáveis de ambiente necessárias.
3. Reinicie o agente. O novo servidor aparecerá na coleta de ferramentas antes do primeiro prompt.

## Troubleshooting rápido

- **`Blocking call` durante o load**: confirme que `langgraph dev` recebeu todas as variáveis (export em vez de ler `.env`).
- **`Missing GEMINI_API_KEY`**: confira `agente_mcp/.env` e reinicie o processo.
- **Weather não responde**: certifique-se de que `python agente_mcp/mcp_servers/weather_server.py` está ativo e que a URL em `servers.py` aponta para o host/porta corretos.
- **Tool-call falhou**: veja o bloco `Run log:` impresso ao final; cada entrada inclui `tool_name`, `status` e mensagem de erro amigável.
