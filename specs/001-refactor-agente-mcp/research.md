# Research: Refatorar agente_mcp

## Decision 1: Graph API modular inspirado em agentes existentes
- **Rationale**: `PROJETOS.md` descreve que `agente_simples`, `agente_tool` e `agente_memoria` compartilham fluxo modular baseado em StateGraph com nodes bem definidos (validate_input → invoke_model → format_response). Adotar o mesmo padrão facilita reutilizar `graph-nodes-patterns.md`, viabiliza checkpoints futuros e mantém compatibilidade com LangGraph Studio. O agente atual já usa Graph API parcialmente, então a refatoração exige menos esforço que migrar para Functional API/Create Agent.
- **Alternatives considered**: (a) Functional API com decorators `@entrypoint/@task` — rejeitada porque o usuário precisa manter `main.py` simples sem alterar paradigma; (b) `create_agent` de LangChain v1 com middleware — descartada pois adicionaria dependência extra e não permitiria controle fino sobre MultiServerMCPClient.

## Decision 2: Perfis declarativos para servidores MCP
- **Rationale**: Centralizar configurações em `ServerProfile` (dataclass + YAML/JSON) permite ativar/desativar servidores sem tocar no grafo, atendendo FR-005 e o User Story P2. A abordagem segue o padrão de `agente_tool`, que isola tools em módulos e facilita trocas controladas. O carregamento declarativo também simplifica logs e validações antes de executar o grafo.
- **Alternatives considered**: (a) Manter configurações hardcoded em `main.py` — não escalável e repete o estado atual; (b) Usar `.env` para cada servidor — tornaria o arquivo difícil de manter e menos explícito sobre parâmetros como transporte/comando.

## Decision 3: Observabilidade com logging estruturado + roteiro de QA manual
- **Rationale**: Como o usuário dispensou testes automatizados, precisamos de logs ricos (timestamp, nível, contexto por tool-call) e um checklist manual (README). `agente_tool` e `agente_memoria` já usam logging estruturado (via `structlog`/`logging`), então replicaremos o padrão com adaptadores reutilizáveis. Isso garante cumprimento de SC-003 sem frameworks adicionais.
- **Alternatives considered**: (a) Introduzir suíte pytest completa — rejeitada pelo usuário; (b) Usar ferramentas externas de observabilidade — desnecessário para escopo local.

## Decision 4: Fluxo manual via `main.py` com prompts configuráveis
- **Rationale**: Constituição (Princípio I) exige `main` funcional, e o usuário explicitamente não quer argparse/Typer. Portanto, encapsularemos o fluxo em funções internas (e.g., `run_demo_session`) que aceitam lista de perguntas (vinda de arquivo/json) mas permitem fallback para input manual. Mantemos compatibilidade com `python agente_mcp/main.py` e podemos adicionar gatilho `if __name__ == "__main__"` para custom prompts.
- **Alternatives considered**: (a) Recriar CLI com argparse/flags — rejeitado pelo usuário; (b) Exigir interface web/REST — fora do escopo.
