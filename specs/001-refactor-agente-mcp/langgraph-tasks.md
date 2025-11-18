# Documento de Tarefa: Refatorar agente_mcp

## 1. Análise Atual
### 1.1 Estado Atual
- **Estrutura**: Código monolítico em `agente_mcp/` com `main.py`, `agent_graph.py`, `common.py` e servidores dentro de `mcp_servers/`, sem separação clara entre config/state/graph/CLI.
- **State Schema**: `State` definido dentro de `agent_graph.py` como `TypedDict` minimalista, sem agregação de metadados, validadores ou reducers adicionais.
- **Nós / Fluxo**: Grafo simples com chatbot + tool node; não há fase explícita de validação, planejamento ou formatação, e chamadas de servidor são gerenciadas diretamente no grafo.
- **CLI / Execução**: `main.py` executa dois prompts sequenciais hardcoded, inicializa `MultiServerMCPClient` inline e não oferece interface reutilizável nem validação de `.env`/servers.
- **Testes**: `tests/test_agente_mcp.py` usa interface `app.invoke`, mas o módulo não exporta `app`; depende de servidores reais e não cobre edge cases ou logs.
- **Observabilidade**: Ausência de logging estruturado, checagem de disponibilidade de servidores ou manuseio consistente de exceções.

### 1.2 Impacto da Mudança
- **Componentes afetados**: Todos os arquivos de `agente_mcp/`, README específico e scripts de servidores MCP.
- **Riscos**: Reintroduzir regressões ao dividir o grafo, divergência entre documentação e implementação, configuração inadequada de servidores externos, aumento de complexidade do fluxo se o `main.py` não for preservado.
- **Mitigações**: Adotar estrutura padrão LangGraph (state/config/utils/graph) mantendo `main.py` como entrypoint único, adicionar validações automatizadas de configuração e documentar fluxos e requisitos de ambiente para facilitar testes manuais.

## 2. Requisitos & Objetivos
### 2.1 Objetivo Principal
Refatorar o agente para seguir boas práticas de Python e organização LangGraph, garantindo executável único (`main.py`), cadastro declarativo de servidores MCP e observabilidade suficiente para testes manuais.

### 2.2 Escolha de API
- **Graph API (StateGraph)**: Mantida para total controle do fluxo multi-servidor e compatibilidade com LangGraph Studio/checkpointing.
- **Functional API / create_agent**: Não aplicadas neste refactor para evitar mudanças bruscas de paradigma; futuras extensões podem considerar `create_agent` com middleware.

### 2.3 Estrutura do Projeto
Adotar estrutura "Básica" (Seção 0.5.1 do template) personalizada para `agente_mcp`, preservando `main.py` como ponto de entrada:
```
agente_mcp/
├── __init__.py
├── config.py
├── state.py
├── graph.py
├── utils/
│   ├── __init__.py
│   ├── servers.py
│   ├── nodes.py
│   ├── logging.py
│   └── prompts.py
├── mcp_servers/
│   ├── __init__.py
│   ├── math_server.py
│   └── weather_server.py
├── main.py
└── docs/
    └── README.md (ou atualizar README existente)
```
Complementar com artefatos de config (`.env.example`, `langgraph.json`) para facilitar execução manual.

## 3. Organização de Arquivos
### 3.1 Estrutura Base
1. **Criar modules** `config.py`, `state.py`, `graph.py`, `utils/` seguindo naming conventions.
2. **Mover** `MultiServerMCPClient` setup para `utils/servers.py` com leitura declarativa (JSON/YAML/dataclass) listando servidores (`math`, `weather`, futuros) e metadados (transporte, endpoint/comando, auto-start, timeout).
3. **Atualizar** `mcp_servers/` para pacote (adicionar `__init__.py`, tipagem e docstrings consistentes).
4. **Adicionar** `.env.example`, `langgraph.json`, `Makefile` ou scripts equivalentes se não existirem.

### 3.2 Padrões de Importação
- **Order**: stdlib → third-party → local.
- **Exports**: `__all__` em `utils/__init__.py` expondo helpers principais.
- **Type hints**: usar `typing_extensions.Annotated`, `TypedDict`, `Literal` conforme necessário.

## 4. Implementação Detalhada
### 4.1 State & Config
1. **state.py**
   - Definir `AgentState` (`messages`, `run_log`, `metadata`, `errors`) com reducers (`add_messages`, merges customizados).
   - Incluir helpers para reset/trim de mensagens.
2. **config.py**
   - Criar `AppConfig` dataclass (env, modelo LLM, temperatura, transporte servers, checkpointer default MemorySaver para dev).
   - Incluir validadores (`validate_env`, `ensure_servers_available`).
   - Expor função `load_config()` que carrega `.env`, valida presença de `GEMINI_API_KEY` e URLs.

### 4.2 Nodes, Tools e Servidores
1. **utils/nodes.py**
   - Separar nodes: `validate_input`, `plan_tools`, `invoke_llm`, `execute_tools`, `format_response`, `handle_error`.
   - Garantir logging contextual em cada node.
2. **utils/servers.py**
   - Definir `ServerProfile` (nome, transporte, endpoint/comando, auto_start, retries).
   - Implementar funções `load_server_profiles()`, `start_required_servers()`, `stop_auto_started_servers()` e `build_mcp_client(profiles)`.
3. **utils/logging.py**
   - Configurar logger padrão (structlog ou logging) com formato `[timestamp] [level] [context] message`.
4. **Prompts / mensagens**
   - Opcional: mover frases padrão para `utils/prompts.py` para facilitar testes.

### 4.3 Graph Construction
1. **graph.py**
   - Função `create_graph(config: AppConfig, client: MultiServerMCPClient)` retornando grafo compilado com checkpointer configurado.
   - Adicionar conditional edges (router) que avaliam tool-calls e fallback para END.
   - Expor `app = create_graph(... )` para uso em `main.py` e futuros scripts automatizados.
2. **Error routing**
   - Implementar `route_errors` ou `handle_error` node para garantir mensagens amigáveis.

### 4.4 Execução via main.py
1. **main.py**
   - Manter `main.py` como entrypoint único, encapsulando carregamento de config, validações, inicialização do grafo e perguntas de teste (ou input manual) em funções reutilizáveis.
   - Substituir código hardcoded por chamadas parametrizáveis (lista de perguntas lida de arquivo/env ou argumentos simples) mantendo simplicidade para execução manual.
2. **Graceful shutdown**
   - Garantir encerramento de servidores auto-start e fechamento de clientes antes de encerrar o script.
3. **Observabilidade**
   - Emitir logs estruturados para cada tool-call (nome, duração, status) e para exceções capturadas, suficientes para depuração manual.

### 4.5 Documentação & Examples
1. Atualizar `agente_mcp/README.md` com nova estrutura, passos (setup `.env`, start servers, comando `python agente_mcp/main.py`), exemplos de perguntas e como observar logs.
2. Adicionar exemplos de configuração de novos servidores MCP usando `ServerProfile`.
3. Documentar edge cases (servidor indisponível, env ausente) e como o script responde para orientar testes manuais.

## 5. Validação Manual
- Preparar roteiro de testes manuais cobrindo: execução básica de `main.py`, adição de novo servidor, indisponibilidade de servidor, ausência de `.env`, tool-call com erro.
- Registrar checklist de passos no README para servir como guia de QA manual (ex.: comandos para iniciar servidores, logs esperados, mensagens de erro).
- Garantir que logs forneçam informações suficientes para depuração sem tooling adicional.

## 6. Deployment & Monitoring
### 6.1 Estrutura Final
- Confirmar `langgraph.json` apontando para `agente_mcp/graph.py:create_graph` e `.env`.
- Criar `Makefile` targets `install`, `run`, `test`, `lint` (opcional mas recomendado pelo template).
- Validar `langgraph dev`/`langgraph run` funcionam com nova estrutura.

### 6.2 Checklist de Pronto para Planejamento
- [ ] Config / state modularizados e documentados.
- [ ] `main.py` preservado como entrypoint com validações e observabilidade.
- [ ] Cadastro declarativo de servidores MCP com auto-start opcional.
- [ ] Logging estruturado para sessões e tool-calls.
- [ ] README + `.env.example` atualizados com roteiro de testes manuais.
- [ ] langgraph.json/Makefile alinhados.
- [ ] Observabilidade básica pronta (logs + mensagens amigáveis).
