# Arquitetura – agente_tool

## Visão Geral

O agente foi refatorado para seguir a estrutura modular adotada pelos demais projetos LangGraph do repositório. O pacote `agente_tool` agora é composto pelos seguintes módulos principais:

- `config.py`: centraliza o carregamento de variáveis de ambiente e criação de dependências (LLM Gemini e `MemorySaver`).
- `state.py`: define `GraphState`, `ThreadConfig` e `ToolPlan`, garantindo contratos claros entre os nodes.
- `utils/`: agrupa utilidades compartilhadas (`nodes.py`, `tools.py`, `logging.py` e reexports em `__init__.py`).
- `graph.py`: constrói o `StateGraph` com roteamento condicional entre validação, planejamento, execução de ferramenta, invocação do modelo e formatação.
- `cli.py`: expõe o comando `python -m agente_tool run "<pergunta>"`, incluindo pré-checagem de configuração e logging estruturado.
- O `SYSTEM_PROMPT` orienta o Gemini a responder em português, chamar a ferramenta `calculator` sempre que precisar computar expressões e, após o ToolMessage, produzir uma explicação breve com o resultado definitivo.

## Fluxo do Grafo

1. **validate_input** (`utils/nodes.py`)  
   Sanitiza a pergunta do usuário, registra metadata (`question`, `started_at`, `system_prompt`) e interrompe o fluxo com mensagem orientativa quando a entrada é muito curta.

2. **invoke_model** (`utils/nodes.py`)  
   Constrói o prompt com o `SystemMessage` descrito no metadata e envia a conversa atual para o Gemini. A resposta pode ser texto direto ou uma chamada para a ferramenta `calculator`.

3. **plan_tool_usage** (`utils/nodes.py`)  
   Analisa o último `AIMessage` retornado pelo modelo e, se houver `tool_calls`, converte o primeiro pedido em um `ToolPlan` (nome, argumentos e identificador da chamada).

4. **execute_tools** (`utils/nodes.py`)  
   Executa a calculadora endurecida com AST sandbox, gera o `ToolMessage`, atualiza metadata (`last_tool_result`) e registra `tool_call` e `resposta` intermediária.

5. **finalize_response** (`utils/nodes.py`)  
   Reinvoca o Gemini após a execução da ferramenta, desta vez com o histórico contendo o `ToolMessage`, para produzir a resposta textual final. Novas solicitações de ferramenta nessa etapa são tratadas como erro controlado.

6. **format_response** (`utils/nodes.py`)  
   Aplica o prefixo `"Resposta do agente:"`, calcula `duration_seconds` e encerra o fluxo com `status="completed"` (ou `"error"` em trajetórias controladas).

O roteamento condicional definido em `graph.py` garante:

- `validate_input` → `format_response` em caso de erro de entrada; caso contrário segue para `invoke_model`.
- `invoke_model` → `format_response` quando ocorre erro ao chamar o modelo, ou `plan_tool_usage` para continuidade normal.
- `plan_tool_usage` → `execute_tools` quando há plano de ferramenta; caso contrário vai direto para `format_response` utilizando a resposta textual do modelo.
- `execute_tools` → `finalize_response`, ou `format_response` se a ferramenta falhar.
- `finalize_response` → `format_response` com a resposta definitiva ao usuário.

## CLI e Persistência

- O comando `run` aceita a pergunta e um `--thread-id` opcional; por padrão utiliza `DEFAULT_THREAD_ID` definido no `.env`.
- A persistência em memória utiliza `MemorySaver`, permitindo retomar conversas na mesma thread.
- Logs são escritos em `stdout` e em `agente_tool/logs/agent.log`, incluindo marcos de validação, planejamento, execução da ferramenta, chamada ao modelo e conclusão.

## Testes

- `agente_tool/tests/test_nodes.py` cobre validação, planejamento, execução da ferramenta, tratamento de erros e formatação.
- `agente_tool/tests/test_graph.py` executa o fluxo completo com um LLM stub que consome o resultado da calculadora.
