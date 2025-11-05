# Implementation Plan: Refactor agente_banco_dados Structure

**Branch**: `023-refactor-db-agent` | **Date**: 2025-11-05 | **Spec**: specs/023-refactor-db-agent/spec.md
**Input**: Feature specification from `/specs/023-refactor-db-agent/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Refatorar o projeto `agente_banco_dados` para adotar a arquitetura modular usada em `agente_simples`, mantendo o relatório SQLite atual e adicionando uma função `create_app()` compatível com LangGraph CLI. A abordagem segue o plano em `langgraph-tasks.md`: extrair nós puros para coletar métricas e renderizar Markdown, reorganizar o pacote em módulos (`state`, `utils/nodes`, `graph`, `cli`) e atualizar documentação e catálogos de nodes sem alterar a lógica existente. O desenho reaproveita padrões descritos em `PROJETOS.md` para `agente_simples` e `agente_banco_dados`, garantindo paridade funcional.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12.3 (venv do repositório)  
**Primary Dependencies**: langgraph, langchain-core, google-generativeai (`gemini-2.5-flash`), python-dotenv, sqlite3 (stdlib), tabulate/textwrap auxiliares conforme necessário  
**Storage**: SQLite local (`agente_banco_dados/data/sales.db`)  
**Testing**: pytest (reutilizando suíte existente e novos testes dedicados ao agente)  
**Target Platform**: Execução local via CLI tradicional e LangGraph CLI  
**Project Type**: Single-agent CLI application  
**Performance Goals**: Relatório gerado em até 10 segundos usando o banco seed (SC-002)  
**Constraints**: Nenhuma mudança funcional perceptível; execução 100% offline com dados locais; docstrings obrigatórias  
**Scale/Scope**: Dataset de exemplo pequeno; um único grafo sequencial sem concorrência

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]
- Docstrings serão acrescentadas ou revisadas para todas as funções criadas/alteradas (Principle XXI) conforme descrito nas tarefas de modularização.
- Caso `langgraph.json` precise registrar o grafo do agente, a atualização será incremental, apenas adicionando a nova entrada sem remover existentes (Principle XXII).
- O plano consulta `graph-nodes-patterns.md` (já refletido em `langgraph-tasks.md`) e inclui tarefa explícita para sincronizar a nomenclatura dos novos nodes `load_sales_metrics` e `render_sales_report` (Principle XXIII).

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
agente_banco_dados/
├── __init__.py
├── config.py
├── db_init.py
├── reporting.py
├── data/
└── main.py                 # (será reduzido a delegar para cli)

agente_simples/             # Referência estrutural (state, graph, cli, utils, tests)
tests/
specs/
graph-nodes-patterns.md     # Catálogo de nomes de nodes compartilhado
```

**Structure Decision**: A refatoração atuará exclusivamente em `agente_banco_dados/`, criando arquivos adicionais (`state.py`, `graph.py`, `cli.py`, `utils/nodes.py`, possivelmente `utils/__init__.py`, testes dedicados) e reorganizando `main.py`/`__init__.py` para expor `create_app()`. Diretórios globais (`tests/`, `specs/`) receberão apenas os artefatos planejados; nenhum novo projeto de topo será adicionado.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
