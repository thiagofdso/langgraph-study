# Implementation Plan: SQLite Sales Agent

**Branch**: `[011-sqlite-sales-agent]` | **Date**: 2025-10-29 | **Spec**: specs/011-sqlite-sales-agent/spec.md
**Input**: Feature specification from `/specs/011-sqlite-sales-agent/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a study-focused LangGraph agent in `agente_banco_dados` that seeds a local SQLite database with products, sellers, and sales data, then generates a markdown sales report (top products and sellers) using only local data—no network usage allowed.

## Technical Context

**Language/Version**: Python 3.12.3 (repo virtualenv)  
**Primary Dependencies**: langgraph, langchain-core, sqlite3 (stdlib), tabulate/markdown handling TBD (likely use `textwrap` or manual formatting)  
**Storage**: Local SQLite database file within `agente_banco_dados`  
**Testing**: Manual execution via `python agente_banco_dados/main.py` (no automated tests requested)  
**Target Platform**: Local CLI execution on Linux/macOS/Windows using repo virtualenv  
**Project Type**: Single-agent CLI project  
**Performance Goals**: Complete seeding and reporting within ~10 seconds for small datasets  
**Constraints**: Strictly offline; zero external network calls; idempotent DB initialization  
**Scale/Scope**: Sample dataset (≤100 records total); single-user study scenario

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Principle I: Ensure `agente_banco_dados/main.py` remains the runnable entry point. ✅
- Principle II & XIII: Must research LangGraph + SQLite practices (use external docs, allowed web search if needed). Pending ➜ handled in Phase 0.
- Principle IV: Default LLM must be `gemini-2.5-flash` within LangGraph configuration. ✅ Plan to comply.
- Principle V: Agent must be built with LangGraph. ✅
- Principle VI: Keep architecture simple—single graph with seeding helper. ✅
- Principle VIII: Use repo `venv` and manage dependencies in appropriate requirements file. ✅
- Principle XII: Copy `.env` template from `agente_simples` for new project. ✅

Gate status: **PASS**, with reminder to document research outcomes before implementation.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Descreva como o repositório está organizado hoje.
  Cada diretório de primeiro nível representa um projeto/experimento independente.
  Ajuste a árvore listando apenas os diretórios relevantes para esta feature.
-->

```text
agente_simples/              # Projeto base (contém .env modelo, main.py simples)
agente_tool/                 # Referência para agentes enxutos (consultar simplicidade)
agente_web/                  # Projeto anterior (web search) para padrões recentes
agente_banco_dados/          # ➜ Novo projeto desta feature (main.py, db_init.py, README.md, .env, etc.)
external_docs/               # Documentações via Context7 (usar langgraph_docs.md para boas práticas)
research/                    # Pesquisas existentes; reutilizar/expandir se necessário
tests/                       # Testes específicos por projeto (não usados aqui)
requirements.txt             # Dependências compartilhadas (avaliar se adicionar langgraph/langchain aqui ou local)
venv/                        # Ambiente virtual Python do repositório
```

**Structure Decision**: Criar o diretório `agente_banco_dados/` contendo `__init__.py`, `main.py`, `db_init.py`, `.env` (cópia de `agente_simples/.env`), `README.md` e arquivos auxiliares (ex.: dados seeds). Reutilizar `requirements.txt` raiz caso dependências já existam; caso contrário, avaliar manter arquivo local simples para estudo. Nenhuma alteração em projetos existentes além de referências cruzadas mínimas.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | - | - |

## Phase 0 – Outline & Research

- **Unknowns to resolve**
  - Confirm recommended LangGraph patterns for deterministic tool pipelines and data access (consult `external_docs/langgraph_docs.md`).
  - Identify best practices for integrating SQLite queries within LangGraph nodes or tools (research via local docs + web if necessary).
  - Determine markdown formatting approach for console-friendly reports (e.g., manual tables vs. helper libs).
- **Research tasks**
  1. Review `external_docs/langgraph_docs.md` for guidance on graph construction, state management, and tool invocation order relevant to local DB usage.
  2. Search for examples of LangGraph agents querying SQLite, focusing on synchronous tool functions and shared state handling.
  3. Evaluate lightweight markdown table generation techniques suited for CLI output without heavy dependencies.
- **Deliverable**: `specs/011-sqlite-sales-agent/research.md` summarizing decisions (decision, rationale, alternatives) and removing any remaining unknowns before design.

## Phase 1 – Design & Internal Interfaces

- **Data Model**: Document simplified entities (Product, Seller, Sale) with necessary fields and relationships in `data-model.md`.
- **Contracts**: No external API; skip `contracts/` output (document rationale in plan and ensure directory remains absent).
- **Quickstart**: Outline step-by-step instructions for running `python agente_banco_dados/main.py`, highlighting `.env` setup and expected console report.
- **Agent Context Update**: Run `.specify/scripts/bash/update-agent-context.sh codex` after confirming new tech decisions (likely no changes beyond referencing SQLite usage).

## Phase 2 – Task Planning (deferred to `/speckit.tasks`)

- Once design artifacts are approved, generate detailed task list aligning with user stories (seed DB, run report). Not covered in this command.
