# Implementation Plan: Terminal Task Session Agent

**Branch**: `[013-task-agent]` | **Date**: 2025-10-30 | **Spec**: [specs/013-task-agent/spec.md](specs/013-task-agent/spec.md)
**Input**: Feature specification from `/specs/013-task-agent/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a study-focused terminal agent under `agente_tarefas/` that guides a learner through exactly three interactions: (1) capturing an initial list of tasks, (2) marking one task as completed, and (3) optionally appending new tasks before presenting a final summary. The implementation will rely on `langgraph` with built-in memory to track task state, integrate `gemini-2.5-flash` via `google-generativeai`, and mirror memory patterns demonstrated in `agente_memoria/main.py` while following langgraph best practices from `external_docs/langgraph_docs.md`.

## Technical Context

**Language/Version**: Python 3.12.3  
**Primary Dependencies**: langgraph, langchain-core, google-generativeai (`gemini-2.5-flash`), python-dotenv (via project standard), standard library I/O utilities  
**Storage**: In-memory session state only (task list and completion markers)  
**Testing**: Manual terminal walkthrough using the scripted three-round flow; no automated tests planned due to LLM interactions  
**Target Platform**: Local terminal (Linux/macOS/Windows) running within project virtualenv  
**Project Type**: Single-file CLI agent project  
**Performance Goals**: Provide each agent response within 5 seconds under normal network conditions (assumed acceptable for study use)  
**Constraints**: Exactly three sequential prompts, no interaction loop, user inputs and agent responses must be echoed to terminal, Portuguese prompts, adhere to langgraph memory guidance, copy `.env` from `agente_simples`  
**Scale/Scope**: Single-user educational demo executed on demand

## Constitution Check

- **Principle I – Main File for Testing**: PASS — Plan delivers executable `agente_tarefas/main.py` as the entry point.  
- **Principle II – Continuous Learning & Best Practices**: PASS — Research step includes reviewing `external_docs/langgraph_docs.md` and memory examples.  
- **Principle IV – Standard LLM Model**: PASS — `gemini-2.5-flash` mandated in design.  
- **Principle V – Standard Agent Framework**: PASS — `langgraph` chosen for orchestration.  
- **Principle VIII – Python Development Standards**: PASS — Work remains in Python, dependencies tracked via repository conventions.  
- **Principle XII – Environment Configuration**: PASS — Plan includes copying `.env` from `agente_simples` into `agente_tarefas`.  
- **Principle XIV – Specification-Driven Development**: PASS — Working from approved spec and plan workflow.  

All gates satisfied; proceed to Phase 0 research.

Post-Phase 1 review (2025-10-30): Design outputs maintain compliance; no new constitutional concerns identified.

## Project Structure

### Documentation (this feature)

```text
specs/013-task-agent/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
agente_memoria/          # Exemplo existente de uso de memória com langgraph
agente_simples/          # Projeto base com convenções de estrutura e .env de referência
agente_tarefas/          # (Novo) Projeto de 3 rodadas com langgraph + Gemini
backend/
external_docs/           # Documentação consultiva (inclui langgraph_docs.md)
frontend/
requirements.txt         # Dependências compartilhadas na raiz
specs/                   # Documentação de features
venv/                    # Ambiente virtual Python 3.12.3
```

**Structure Decision**: Criar novo diretório `agente_tarefas/` contendo `__init__.py`, `main.py`, `.env` copiado de `agente_simples`, e README resumido; manter demais projetos intactos e seguir padrão de single-entry-point.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
