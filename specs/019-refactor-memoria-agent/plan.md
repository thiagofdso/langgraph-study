# Implementation Plan: Refactor Memory Agent

**Branch**: `019-refactor-memoria-agent` | **Date**: November 1, 2025 | **Spec**: specs/019-refactor-memoria-agent/spec.md
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Refatorar `agente_memoria` para oferecer conversas multi-turno com memória, diagnósticos de configuração e registros operacionais, reorganizando o código segundo o padrão modular do `agente_simples`. A abordagem reutiliza o modelo `gemini-2.5-flash`, LangGraph `StateGraph` com checkpointer em memória e estrutura em camadas (config, state, nodes, graph, CLI), garantindo docstrings e testes orientados a nodes/fluxo.

## Technical Context

**Language/Version**: Python 3.12.3  
**Primary Dependencies**: langgraph, langchain-core, langchain_google_genai (ChatGoogleGenerativeAI), python-dotenv, typing_extensions, pydantic  
**Storage**: LangGraph InMemorySaver (padrão), com possibilidade futura de substituição por store persistente  
**Testing**: pytest com fixtures simulando LLM e checkpointer  
**Target Platform**: CLI local em ambiente Linux/macOS com acesso à internet  
**Project Type**: Projeto único de agente (estrutura modular interna)  
**Performance Goals**: Respostas multi-turno em ≤12s, onboarding completo em ≤10 minutos, verificação automatizada ≤5 minutos  
**Constraints**: Uso exclusivo de `gemini-2.5-flash`, mensagens e documentação em português, docstrings obrigatórios, evitar mutação direta do estado  
**Scale/Scope**: Agente demonstrativo para equipe interna, uso por dezenas de operadores simultâneos via threads isolados

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]
- Confirm documentation plan ensures every new or modified function includes uma docstring descritiva (Principle XXI) — cumprir adicionando docstrings a todos os nodes, utilidades e classe de configuração gerados.
- Pós-Fase 1: Revisão manteve compromisso com docstrings; nenhuma exceção planejada.

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
agente_memoria/            # Agente alvo da refatoração; hoje possui main.py único e README
agente_simples/            # Referência direta para estrutura modular (config, graph, state, utils, tests)
agente_reflexao_web/
agente_tool/
agente_web/
multi_agentes_*            # Exemplos multiagente (não tocados nesta feature)
specs/                     # Diretório de especificações e planos (019-refactor-memoria-agent em foco)
tests/                     # Pasta genérica; projetos costumam manter testes próprios internamente
requirements.txt           # Dependências compartilhadas
venv/                      # Ambiente virtual Python para execução local
```

**Structure Decision**: Reestruturar `agente_memoria/` para refletir o layout modular do `agente_simples`, criando arquivos `config.py`, `state.py`, `graph.py`, `cli.py`, subpasta `utils/` (nodes, logging, __init__), subpasta `docs/`, suíte `tests/` dedicada e arquivos auxiliares (`prompts.py`, `.env.example`, `langgraph.json`). Nenhum novo projeto de nível superior será adicionado; mudanças concentram-se no pacote existente.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
