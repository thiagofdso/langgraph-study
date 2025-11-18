# Implementation Plan: Refatorar agente_mcp

**Branch**: `001-refactor-agente-mcp` | **Date**: 2025-11-18 | **Spec**: [/specs/001-refactor-agente-mcp/spec.md](spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Refatoraremos `agente_mcp` para seguir o padrão modular usado em `agente_simples`, `agente_tool` e `agente_memoria` descritos em `PROJETOS.md`: módulos dedicados para `config`, `state`, `graph`, `utils/` e servidores MCP separados. O `main.py` continuará sendo o ponto único de execução/manual QA, mas agora carregará configurações validadas, iniciará servidores declarados e orquestrará o `StateGraph` com nodes especializados (validação, invocação do LLM Gemini 2.5, execução de ferramentas e formatação). A configuração de servidores será declarativa (dataclasses/JSON) para facilitar adições sem mexer no grafo, e o README + `.env.example` fornecerão roteiro de teste manual (0-10 minutos) inspirado no fluxo documentado para `agente_tool`.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12.3 (repo venv)  
**Primary Dependencies**: langgraph, langchain-core, langchain_mcp_adapters (MultiServerMCPClient), google-generativeai (`gemini-2.5-flash`), dotenv, structlog/logging  
**Storage**: N/A (in-memory state + `.env` for credentials)  
**Testing**: Manual smoke tests via `python agente_mcp/main.py` (no automated pytest at user request)  
**Target Platform**: Local Linux/macOS dev shell (PYTHONPATH-based execution)  
**Project Type**: Single-agent LangGraph project (CLI-like script)  
**Performance Goals**: Setup+run experience <10 min (SC-001); logs emitted for 100% tool-calls (SC-004); manual sessions finish without hanging servers  
**Constraints**: Must keep `main.py` as executable entry (Constitution I); no argparse/Typer CLI; manual QA only; default LLM must remain Gemini 2.5 (Constitution IV)  
**Scale/Scope**: Single developer environments; handful of concurrent sessions (thread_id separation) and 2-3 MCP servers initially (math/weather + future additions)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Docstrings: Todos os novos módulos (`config.py`, `state.py`, `graph.py`, `utils/*`, `main.py`) incluirão docstrings por função/nó, alinhados ao plano de documentação (Princípio XXI).  
- `langgraph.json`: Atualizaremos acrescentando a referência ao grafo refatorado (`agente_mcp/graph.py:create_graph`) sem remover registros existentes, respeitando o princípio XXII.  
- Node naming: Antes de renomear/criar nodes (e.g., `validate_input`, `execute_tools`, `format_response`), consultaremos `graph-nodes-patterns.md` para reutilizar nomes existentes e documentar novos padrões se necessário (Princípio XXIII).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
├── langgraph-tasks.md   # Output from /langgraph.create-tasks command
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Descreva como o repositório está organizado hoje.
  Cada diretório de primeiro nível representa um projeto/experimento independente.
  Ajuste a árvore listando apenas os diretórios relevantes para esta feature.
-->

```text
agente_simples/            # Referência de estrutura modular (config/state/graph/cli)
agente_tool/               # Agente com fluxo tool planner; serve de inspiração p/ nodes/logging
agente_memoria/            # Outro exemplo de StateGraph com MemorySaver
agente_mcp/                # Projeto alvo da refatoração
multi_agentes_*/           # Demais experimentos (sem impacto direto)
specs/                     # Diretórios de especificação gerados pelo .specify
tests/                     # Testes legados (não serão ampliados para este projeto)
requirements.txt           # Dependências comuns (langgraph, langchain, google-generativeai, etc.)
venv/                      # Ambiente virtual Python 3.12.3 usado em toda a árvore
```

**Structure Decision**: Atualizaremos apenas `agente_mcp/`, adicionando `config.py`, `state.py`, `graph.py`, `utils/` e reorganizando `main.py` + `mcp_servers/`. Nenhum novo projeto raiz será criado. `langgraph.json`, `.env.example` e `README.md` do `agente_mcp` serão ajustados para refletir o fluxo manual. Outros diretórios permanecem intactos, exceto a inclusão dos artefatos de planejamento em `specs/001-refactor-agente-mcp/`.

## Phase 0 – Research Summary
- `research.md` documenta quatro decisões principais: manter Graph API modular (inspirado em `agente_simples/agente_tool`), introduzir `ServerProfile` declarativo, reforçar observabilidade/logging para compensar a ausência de testes automatizados e preservar `main.py` como fluxo manual configurável.
- Todas as ambiguidades do contexto técnico (CLI, testes, servidor declarativo) foram resolvidas sem NEEDS CLARIFICATION adicionais.

## Phase 1 – Design Outputs
- `data-model.md` define `AgentSession`, `ServerProfile` e `ExecutionConfig`, com validações e relacionamentos diretos aos requisitos FR-001/FR-005/FR-008.
- `/contracts/manual-run.yaml` modela os fluxos equivalentes (executar sessão e gerenciar servidores) como endpoints REST, garantindo que documentamos expectativas de entrada/saída para futuros wrappers.
- `quickstart.md` fornece roteiro em cinco passos (setup → servidores → execução → extensão → troubleshooting) cobrindo SC-001 e o plano de validação manual.
- `.specify/scripts/bash/update-agent-context.sh codex` foi executado para incluir linguagem/dependências no `AGENTS.md`, mantendo o alinhamento institucional.

## Constitution Re-check (Post Phase 1)
- Docstrings seguirão obrigatórios em todos os arquivos novos, confirmado com as decisões de design.
- `langgraph.json` será apenas estendido; o plano não remove entradas existentes.
- A lista de nodes planejados já foi cruzada com `graph-nodes-patterns.md`; novos nomes (se surgirem) serão documentados após implementação.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
