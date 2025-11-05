# Implementation Plan: Refactor agente_imagem Structure

**Branch**: `022-refactor-image-agent` | **Date**: 2025-11-05 | **Spec**: [specs/022-refactor-image-agent/spec.md](specs/022-refactor-image-agent/spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Reestruturar o projeto `agente_imagem` preservando o comportamento multimodal atual, mas adotando a arquitetura modular utilizada no `agente_simples` (config/state/utils/graph/cli/tests) e expondo uma fábrica `create_app()` compatível com o LangGraph CLI. A referência de padrões vem de `PROJETOS.md` (seções `agente_imagem` e `agente_simples`) e do plano de tarefas em `langgraph-tasks.md`, que estabelece nodes alinhados ao catálogo (`validate_input`, `prepare_image`, `invoke_model`, `format_response`) e garante documentação/testes equivalentes.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12.3  
**Primary Dependencies**: langgraph, langchain-core, langchain_google_genai (Gemini 2.5), Pillow, python-dotenv  
**Storage**: N/A (sem persistência; fluxo em memória)  
**Testing**: pytest com mocks de Gemini para garantir determinismo  
**Target Platform**: Execução local via CLI / LangGraph CLI em ambiente Linux  
**Project Type**: Agente único (single-agent) em estrutura modular  
**Performance Goals**: Processar a imagem de referência dentro do tempo atual (< 60s) sem regressões perceptíveis  
**Constraints**: Manter paridade funcional (mesmos logs e respostas), seguir nomenclatura de nodes catalogada, nenhuma alteração nas dependências externas  
**Scale/Scope**: Código e testes restritos ao pacote `agente_imagem` e ajustes incrementais em `langgraph.json`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]
- Confirmar que cada nova função ou função modificada terá docstring cobrindo propósito e retornos (Princípio XXI).
- Confirmar que a inclusão de `agente_imagem` em `langgraph.json` será feita por adição sem alterar entradas existentes (Princípio XXII).
- Confirmar que o plano reutiliza nomes `validate_input`, `invoke_model`, `format_response` e registra qualquer novo node (`prepare_image`) em `graph-nodes-patterns.md` se não existir (Princípio XXIII).

**Reavaliação Após Fase 1**: Os artefatos criados (research, data-model, contratos, quickstart) mantêm as promessas acima sem identificar violações adicionais.

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
agente_simples/            # Referência modular com config/state/utils/graph/cli/tests
agente_imagem/             # Alvo da refatoração (atualmente monolítico em main.py)
agente_tool/
agente_web/
...
external_docs/             # Documentação de apoio (Context7)
specs/                     # Especificações, planos e pesquisas gerados via .specify
tests/                     # Testes compartilhados; inclui cenários para múltiplos agentes
requirements.txt           # Dependências compartilhadas
venv/                      # Ambiente Python padrão do repositório
```

**Structure Decision**: Modularizar `agente_imagem/` criando `config.py`, `state.py`, `graph.py`, `cli.py`, `__main__.py`, `utils/` (nodes, io, logging), e mover testes dedicados para `tests/test_agente_imagem.py`, seguindo o mesmo padrão adotado em `agente_simples`. Atualizar `langgraph.json` apenas para registrar o novo grafo `agente-imagem`, mantendo demais projetos inalterados.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
