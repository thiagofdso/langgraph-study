# Implementation Plan: Relatório de Vendas com Insights Gemini

**Branch**: `001-gemini-sales-report` | **Date**: 2025-11-05 | **Spec**: `specs/001-gemini-sales-report/spec.md`
**Input**: Feature specification from `/specs/001-gemini-sales-report/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Transformar o `agente_banco_dados` para que o relatório inclua narrativa analítica gerada pela Gemini com base nos dados do SQLite, entregando pelo menos três insights acionáveis, conforme o spec. A abordagem seguirá o padrão modular já empregado em `agente_simples` (ver `PROJETOS.md`), reutilizando sua estratégia de configuração LLM e adicionando um nó intermediário inspirado no catálogo de nodes para gerar insights antes da composição final do relatório. As instruções detalhadas do `langgraph-tasks.md` orientam a criação de utilitários (`utils/llm.py`, `utils/prompts.py`) e a atualização do fluxo do grafo.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12.3  
**Primary Dependencies**: langgraph, langchain-core, langchain_google_genai, python-dotenv, sqlite3 (stdlib), tabulate/textwrap (stdlib utilities)  
**Storage**: SQLite local (`agente_banco_dados/data/sales.db`)  
**Testing**: pytest with monkeypatches/stubs for LLM interactions  
**Target Platform**: CLI execution on Linux/macOS environments (via `python -m agente_banco_dados.cli`)  
**Project Type**: Single-agent CLI project  
**Performance Goals**: Relatório entregue com IA em até 30 segundos (SC-002)  
**Constraints**: Mensagens de erro compreensíveis para falhas de IA, geração de pelo menos três insights com referências numéricas, operação offline exceto pela chamada ao Gemini  
**Scale/Scope**: Uso interno por time de vendas, execução sob demanda (single user por execução)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]
- Confirm documentation plan ensures every new or modified function includes uma docstring descritiva (Principle XXI). ✅ Planejado: novas funções (`generate_sales_insights`, prompt builders, nodes) já serão criadas com docstrings.
- Confirm any required update to `langgraph.json` appends new agents without removing existing registrations (Principle XXII). ✅ Nenhuma alteração prevista em `langgraph.json`; somente reutilização do agente existente.
- Confirm planejamento de novos nodes consulta `graph-nodes-patterns.md` e prevê atualização do catálogo se surgirem responsabilidades inéditas (Principle XXIII). ✅ Consultado catálogo; adicionaremos o node `generate_insights` e atualizaremos `graph-nodes-patterns.md` caso a responsabilidade não exista.

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

**Structure Decision**: Somente o pacote existente `agente_banco_dados/` será modificado. Serão adicionados dois módulos utilitários (`utils/llm.py`, `utils/prompts.py`) e ampliados `state.py`, `config.py`, `utils/nodes.py` e `graph.py` seguindo o padrão modular reaproveitado dos demais agentes. `graph-nodes-patterns.md` receberá entrada para o novo node `generate_insights` garantindo consistência com o catálogo institucional.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| _None_ | — | — |

## Phase 0 — Research
- Reviewed `langgraph-tasks.md` to map módulos obrigatórios (LLM factory, prompts) e passos de auditoria.
- Analysed `agente_simples` configuration pattern para replicar criação de LLM e tratamento de credenciais.
- Confirmed necessidade de novo node `generate_insights` e atualização de `graph-nodes-patterns.md`.
- Output: `research.md` consolidando decisões e alternativas (nenhuma pendência de clarificação).

## Phase 1 — Design & Contracts
- Documented entidades e validações em `data-model.md`, cobrindo novos campos de insights e metadados.
- Formalized CLI output expectations em `contracts/report.md` para suportar QA automatizado.
- Escreveu `quickstart.md` orientando configuração de ambiente e validação de erros de IA.
- Executou `.specify/scripts/bash/update-agent-context.sh codex`, sincronizando o contexto do agente Codex com linguagem, frameworks e banco relevantes.

## Constitution Check (Post-Design)
- Principle XXI (Docstrings): Plano mantém meta de criar docstrings para todas as novas funções utilitárias e nodes — nenhum risco identificado.
- Principle XXII (langgraph.json): Nenhuma modificação planejada; catálogo permanece íntegro.
- Principle XXIII (Node naming): Inserção do node `generate_insights` será acompanhada da atualização em `graph-nodes-patterns.md`, garantindo consistência.
