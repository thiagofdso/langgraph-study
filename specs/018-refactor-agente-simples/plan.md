# Implementation Plan: Refactor Simple Agent

**Branch**: `018-refactor-agente-simples` | **Date**: November 1, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Reestruturar o `agente_simples` em uma arquitetura modular com arquivos dedicados para state, config, nodes, logging e CLI, garantindo validação de entrada, mensagens amigáveis e rastreabilidade por logs. O projeto continua usando LangGraph com `gemini-2.5-flash` como modelo padrão, inspirado nos padrões catalogados em `PROJETOS.md` (especialmente `agente_memoria` para uso de `add_messages`, `agente_tool` para separação de nodes e `agente_web` para logging e documentação). A abordagem técnica organiza o código em submódulos, adiciona testes unitários/integrados e atualiza documentação e artefatos de configuração.

## Technical Context

**Language/Version**: Python 3.12.3  
**Primary Dependencies**: langgraph, langchain-core, google-generativeai (`ChatGoogleGenerativeAI`), python-dotenv  
**Storage**: Nenhum (estado em memória, logs em arquivo local)  
**Testing**: pytest (com mocks para LLM)  
**Target Platform**: CLI em ambiente Linux/Unix (execução via `python -m agente_simples`)  
**Project Type**: Projeto single-agent (console)  
**Performance Goals**: 95% das perguntas respondidas em ≤10 segundos; onboarding concluído em ≤15 minutos (conforme spec)  
**Constraints**: Sem stack traces para o usuário; mensagens e documentação em português; configuração via `.env` obrigatória; usar `gemini-2.5-flash` por padrão  
**Scale/Scope**: Um agente único mantido por equipe pequena, com expectativa de evoluir para fluxos adicionais e integração futura com LangSmith

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Main File for Testing)**: Plano preserva entrypoint executável (`cli.py` + `__main__.py`) para executar o agente via CLI.  
- **Principle II (Continuous Learning)**: Fase de pesquisa (Phase 0) incluirá melhores práticas de LangGraph/Google Generative AI.  
- **Principle IV (Standard LLM Model)**: Configuração fixa `gemini-2.5-flash` com flexibilidade documentada.  
- **Principle V (Standard Agent Framework)**: LangGraph permanece como framework central.  
- **Principle VII (Documentation & Comments)**: Operações e README atualizados com justificativas e instruções.  
- **Principle XIV & XX (Specification-Driven + Referencing Prior Projects)**: Plano baseado na spec e referências dos projetos catalogados.  

All gates satisfied; nenhuma violação antecipada.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
├── langgraph-tasks.md   # output (/langgraph.create-tasks command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
```text
agente_simples/                # Projeto alvo da refatoração
agente_tool/                   # Exemplos com separação de nodes/tools
agente_memoria/                # Referência para uso de add_messages e memória
agente_web/                    # Referência para logging e documentação
external_docs/
research/
tests/
requirements.txt
venv/
```

**Structure Decision**: O diretório `agente_simples/` será reorganizado em pacote modular contendo `config.py`, `state.py`, `graph.py`, `cli.py`, subpasta `utils/` (nodes, logging, prompts) e pasta `tests/` dedicada. O arquivo `main.py` atual será substituído por `cli.py` + `__main__.py`, mantendo o fluxo compatível com outros projetos do repositório. Documentação adicional permanecerá em `specs/018-refactor-agente-simples/` e `agente_simples/docs/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
