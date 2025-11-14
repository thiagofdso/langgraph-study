# Implementation Plan: Reestruturar Agente Perguntas

**Branch**: `001-refactor-agente-perguntas` | **Date**: 2025-11-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-refactor-agente-perguntas/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

A refatoração reorganiza `agente_perguntas` para seguir o padrão modular já consolidado em `agente_simples` e `agente_banco_dados`, mantendo a execução interativa via `python -m agente_perguntas`. A estrutura alvo (detalhada em `langgraph-tasks.md`) cria módulos dedicados para configuração, estado, grafo, CLI, utilitários e testes, preservando o fluxo HITL com `interrupt`. Reaproveitaremos convenções documentadas em `PROJETOS.md` para logging estruturado, validação de configuração e organização de testes, garantindo paridade funcional com o projeto atual enquanto habilitamos documentação operacional e `.env.example`.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12 (repo venv)  
**Primary Dependencies**: langgraph, langchain-core, google-generativeai (`gemini-2.5-flash`), structlog/logging stdlib, pytest  
**Storage**: N/A (FAQ em memória + logs em disco local)  
**Testing**: pytest com fixtures/mocks para `interrupt` e logging  
**Target Platform**: Execução local via CLI (Linux/macOS, ambiente de desenvolvimento)  
**Project Type**: CLI single-agent LangGraph package  
**Performance Goals**: Responder perguntas elegíveis em até 5s e rodar suíte `pytest agente_perguntas/tests` em <90s  
**Constraints**: Manter HITL via CLI, validar configuração antes de iniciar grafo, gerar logs em PT-BR, evitar dependências externas além das já adotadas  
**Scale/Scope**: Refatoração de um agente único com documentação, testes e tooling alinhados ao padrão interno

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]
- Confirmamos que toda função/método novo a ser criado (CLI, nodes, helpers) terá docstrings descrevendo propósito, entradas e saídas (Princípio XXI). Docstrings existentes serão revisadas durante implementação.
- Não há alteração prevista em `langgraph.json`; se for necessário registrar o agente futuramente, o plano é apenas acrescentar a entrada mantendo registros existentes (Princípio XXII).
- A redefinição dos nodes seguirá o catálogo em `graph-nodes-patterns.md`; antes de nomear/renomear nodes avaliaremos padrões existentes e atualizaremos o arquivo caso surja responsabilidade inédita (Princípio XXIII).

**Re-evaluation (após Phase 1)**: Nenhum requisito adicional afeta os princípios acima; os artefatos planejados (docstrings, ausência de alterações em `langgraph.json`, consulta aos padrões de nodes) permanecem viáveis.

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

**Structure Decision**: Manteremos `agente_perguntas/` como pacote raiz, criando submódulos (`config.py`, `state.py`, `graph.py`, `cli.py`, `__main__.py`, `utils/`, `tests/`, `docs/`) conforme descrito em `langgraph-tasks.md`. Serão adicionados `.env.example` e diretório de logs criado em runtime. Nenhum outro projeto de nível superior será alterado; apenas este pacote será reorganizado alinhado ao padrão aplicado em `agente_simples` e registrado em `PROJETOS.md`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
