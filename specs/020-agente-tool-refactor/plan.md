# Implementation Plan: Refatorar agente_tool

**Branch**: `020-agente-tool-refactor` | **Date**: 2025-11-04 | **Spec**: `/specs/020-agente-tool-refactor/spec.md`
**Input**: Feature specification from `/specs/020-agente-tool-refactor/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Refatoraremos `agente_tool` para espelhar a estrutura modular dos agentes `agente_simples` e `agente_memoria`, preservando o fluxo original de perguntas matemáticas com delegação à ferramenta calculadora. A remodelagem seguirá o roteiro detalhado em `langgraph-tasks.md`, garantindo atualização do catálogo `graph-nodes-patterns.md`, criação de documentação de baseline/arquitetura e cobertura de testes para validação, tool routing e formatação de respostas.

## Technical Context

**Language/Version**: Python 3.12.3  
**Primary Dependencies**: langgraph, langchain-core, langchain_google_genai, python-dotenv, pytest  
**Storage**: In-memory (LangGraph MemorySaver checkpointer)  
**Testing**: pytest (unit + integration for nodes e graph)  
**Target Platform**: CLI executável local (venv Python)  
**Project Type**: Single-agent LangGraph project  
**Performance Goals**: Responder consultas matemáticas simples em <2 s mantendo formatação “Resposta do agente: …”  
**Constraints**: Manter comportamento funcional original, bloquear execuções inseguras no cálculo, garantir docstrings e logging em nodes críticos  
**Scale/Scope**: Uso individual/local para experimentos; nenhuma integração externa além do modelo Gemini e tool calculator

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]
- Confirm documentation plan ensures every new or modified function includes a descriptive docstring (Principle XXI).
- Confirm any required update to `langgraph.json` appends new agents without removing existing registrations (Principle XXII).
- Confirm planejamento de novos nodes consulta `graph-nodes-patterns.md` e prevê atualização do catálogo se surgirem responsabilidades inéditas (Principle XXIII).

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
```text
agente_simples/            # Projeto de exemplo; projetos incluem __init__.py, main.py, .env, README.md etc.
agente_tool/
agente_web/                # (Adicionar/atualizar conforme a feature)
...
external_docs/             # Documentações coletadas via Context7
research/                  # Pesquisas e anotações de Perplexity ou web search
tests/                     # Conjunto de testes por projeto (quando aplicável)
requirements.txt           # Dependências compartilhadas na raiz (alguns projetos têm o próprio requirements.txt)
venv/                      # Ambiente virtual Python usado em todos os projetos
```

**Structure Decision**: Reorganizar `agente_tool/` para conter `graph.py`, `state.py`, `config.py`, `cli.py` e pacote `utils/` (nodes, tools, logging), adicionar `docs/` com baseline/arquitetura, criar `tests/` dedicados e `.env.example`. Atualizaremos `langgraph.json` adicionando o novo grafo de forma incremental e manteremos `graph-nodes-patterns.md` sincronizado com os nodes do projeto.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
