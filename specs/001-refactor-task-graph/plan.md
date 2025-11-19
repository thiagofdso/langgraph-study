# Implementation Plan: Graph-Managed Task Workflow

**Branch**: `001-refactor-task-graph` | **Date**: 2025-11-19 | **Spec**: `/specs/001-refactor-task-graph/spec.md`
**Input**: Feature specification from `/specs/001-refactor-task-graph/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Refatorar `agente_tarefas` para que as três rodadas do fluxo (ingestão, conclusão, acréscimo) sejam processadas inteiramente por nodes do LangGraph, deixando o CLI como uma camada fina de entrada/saída e garantindo paridade com `langgraph run agente-tarefas`. O plano reaproveita padrões já usados em `agente_memoria` e `agente_imagem` (PROJETOS.md) sobre grafos sequenciais com checkpointer in-memory, expandindo-os com nodes adicionais descritos em `langgraph-tasks.md` e seguindo o catálogo `graph-nodes-patterns.md` para nomenclatura.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12.3 (repo venv)  
**Primary Dependencies**: LangGraph (StateGraph API), langchain-core, langchain_google_genai (Gemini `gemini-2.5-flash`), structlog/logging utilities  
**Storage**: LangGraph checkpointer provided by `AppConfig.create_checkpointer()` (MemorySaver in dev)  
**Testing**: `pytest agente_tarefas/tests`, smoke test via `python -m agente_tarefas`, manual `langgraph run agente-tarefas` validation  
**Target Platform**: Local CLI execution on Linux/macOS plus LangGraph CLI/runtime  
**Project Type**: Single-agent CLI workflow (three-round assistant)  
**Performance Goals**: Deterministic state transitions per rodada; zero divergence between CLI and LangGraph CLI outputs; maintain <1s overhead per rodada compared to current build  
**Constraints**: Must preserve existing prompts/UX, reuse current `.env` expectations, keep compatibility with LangGraph checkpointer semantics, and avoid introducing external services  
**Scale/Scope**: Single agent instance per thread_id; 3 sequential nodes plus optional summary node; affects `agente_tarefas` package only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]
- **Docstrings (Principle XXI)**: Todos os novos nodes/helpers terão docstrings descrevendo inputs/outputs; revisão inclusive para funções existentes tocadas.
- **langgraph.json (Principle XXII)**: A feature não cria novos agentes; se ajustes forem necessários, serão sempre aditivos sem remoção de entradas.
- **Node Naming Playbook (Principle XXIII)**: Padrões atuais de `graph-nodes-patterns.md` serão consultados antes de nomear `prepare_tasks`, `complete_task`, `append_tasks` e o arquivo será atualizado caso o padrão "three-round task orchestration" ainda não exista.

**Re-evaluation after Phase 1**: Mantemos o compromisso de adicionar docstrings para nodes/helpers, nenhuma modificação estrutural em `langgraph.json` é prevista, e o catálogo de nodes será atualizado caso introduzamos nomes inéditos — portanto todos os gates seguem aprovados.

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
agente_tarefas/            # Projeto alvo: CLI, graph, state, config, utils, tests
agente_simples/            # Referência de arquitetura sequencial
agente_memoria/            # Referência para grafos multi-node com checkpointer
agente_imagem/             # Referência para CLI + LangGraph CLI paridade
specs/001-refactor-task-graph/   # Documentação desta feature (spec, plan, research, etc.)
external_docs/, research/  # Referências adicionais
requirements.txt, venv/    # Ambiente Python compartilhado
```

**Structure Decision**: Apenas `agente_tarefas/` será modificado (graph, cli, utils, tests); demais projetos permanecem referências. Documentos adicionais residem em `specs/001-refactor-task-graph/` conforme fluxo `.specify`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
