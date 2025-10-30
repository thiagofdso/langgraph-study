# Implementation Plan: Iterative Reflection Agent Guidance

**Branch**: `014-add-reflection-agent` | **Date**: October 30, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-add-reflection-agent/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement `agente_reflexao_basica/main.py` como script único que usa LangGraph `StateGraph` para alternar nós de geração e reflexão, limitar o fluxo por contagem de mensagens e imprimir rascunhos/reflexões diretamente no console.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12.3  
**Primary Dependencies**: LangGraph, langchain-core, google-generativeai (`gemini-2.5-flash`), python-dotenv  
**Storage**: None (in-memory session state only)  
**Testing**: Manual execution via `python main.py` (no automated tests per requirement)  
**Target Platform**: Local CLI execution on developer workstation  
**Project Type**: Single-run agent project under repository root  
**Performance Goals**: Complete default run in < 60 seconds; final answer cites ≥ 4 learning priorities; reflections count matches configured iterations  
**Constraints**: Must use LangGraph; no new runtime parameters; no interactive loop; preserve copied `.env`; expose reflections and drafts for review  
**Scale/Scope**: Single agent workflow, single fixed question, limited to basic reflection cycle

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I – Main File for Testing**: Plan ensures `agente_reflexao_basica/main.py` remains the runnable entry point for demonstrations. **Pass**
- **Principle II – Continuous Learning & Best Practices**: Research tasks will consult `external_docs/langgraph_docs.md` and LangChain blog on reflection agents before design. **Pass (pending Phase 0 completion)**
- **Principle IV – Standard LLM Model**: Will configure `gemini-2.5-flash` as default model. **Pass**
- **Principle V – Standard Agent Framework**: LangGraph selected as required orchestration framework. **Pass**
- **Principle XII – Environment Configuration**: `.env` copied from `agente_simples` and left untouched per requirement. **Pass**
- **Principle XV – Project Catalog Updates**: Implementation plan notes follow-up to register project in `PROJETOS.md` after completion. **Pass**

_Post-Phase 1 review: No new violations identified; gates remain satisfied._

## Project Structure

### Documentation (this feature)

```text
specs/014-add-reflection-agent/
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
agente_simples/             # Projeto base; fonte para .env padrão e estrutura de agente simples
agente_tool/                # Agente com integrações de ferramentas
agente_web/                 # Agente focado em web search
agente_tarefas/             # Projecto recente com LangGraph e Gemini
multi_agentes_orquestracao/ # Estudos multiagente
external_docs/              # Documentação de referência (inclui langgraph_docs.md)
research/                   # Saídas de investigações anteriores
specs/                      # Especificações, planos e artefatos por feature
tests/                      # Testes compartilhados (não utilizados nesta feature)
requirements.txt            # Dependências compartilhadas
venv/                       # Ambiente virtual Python 3.12.3
```

**Structure Decision**: Utilizar apenas o arquivo `agente_reflexao_basica/main.py`, seguindo o padrão dos projetos sequenciais existentes, e manter `.env` copiado de `agente_simples`. Atualizar `PROJETOS.md` ao concluir para cumprir a Constituição XV.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
