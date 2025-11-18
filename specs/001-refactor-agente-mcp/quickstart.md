# Quickstart: agente_mcp refatorado

## 1. Preparar ambiente
1. Ative o venv raiz (`source venv/bin/activate`).
2. Copie `agente_mcp/.env.example` para `agente_mcp/.env` e preencha no mínimo `GEMINI_API_KEY`.
3. Instale dependências (`pip install -r requirements.txt`).

## 2. Configurar servidores MCP
1. Confira `agente_mcp/utils/servers.py`: os perfis `math` (stdio, auto-start) e `weather` (SSE, manual) já apontam para `agente_mcp/mcp_servers/*`.
2. Inicie o servidor weather manualmente:
   ```bash
   source venv/bin/activate
   python agente_mcp/mcp_servers/weather_server.py
   ```
   Deixe o processo ativo durante os testes.
3. Ajuste endpoints apenas se o host/porta forem diferentes do padrão.

## 3. Rodar sessão manual (CLI)
1. Execute `python -m agente_mcp` para usar as perguntas definidas em `MCP_DEFAULT_QUESTIONS`.
2. Opcional: forneça um `thread_id` específico (`python -m agente_mcp suporte-qa`). Esse mesmo valor é usado no run log e nos históricos do LangGraph.
3. Observe o terminal: para cada pergunta o script imprime `User:`/`Assistant:` e um resumo do `run_log` (fase, ferramenta, status, duração).

## 4. Usar via LangGraph dev
1. Exporte `GEMINI_API_KEY` (o runtime não lê `.env` automaticamente).
2. Rode `langgraph dev` na raiz do repositório; o grafo `agente-mcp` é carregado via `langgraph.json`.
3. Use a interface (ou API) para criar um thread, enviar mensagens e acompanhar tool-calls. O campo `thread_id` informado na UI é preservado pelo agente.

## 5. Adicionar novo servidor
1. Crie `agente_mcp/mcp_servers/<nome>_server.py` usando o padrão FastMCP.
2. Declare o novo `ServerProfile` no vetor `builtin_server_profiles()` (nome único + transporte + endpoint).
3. Reinicie o agente. Verifique nos logs (`server=<nome>`) que as ferramentas foram carregadas antes de rodar perguntas.

## 6. Troubleshooting rápido
- **`Missing GEMINI_API_KEY`**: confira `agente_mcp/.env` (CLI) ou exporte a variável (LangGraph dev).
- **Weather sem resposta**: confirme se o servidor SSE está rodando e se a URL em `servers.py` está correta.
- **BlockingError no LangGraph dev**: garanta que o servidor weather e o agente foram reiniciados após mudar dependências; o grafo já evita I/O bloqueante.
- **Tool-call falhou**: veja o `run_log` impresso ao fim da pergunta; a coluna `message` aponta o erro reportado pelo MCP.
