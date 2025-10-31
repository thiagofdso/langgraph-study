# Implementation Plan: Reflexion Web Evidence Agent

**Branch**: `016-add-reflexion-web` | **Date**: October 31, 2025 | **Spec**: [specs/016-add-reflexion-web/spec.md](specs/016-add-reflexion-web/spec.md)
**Input**: Feature specification from `/specs/016-add-reflexion-web/spec.md`

**Note**: This plan is an integral part of the specification-driven development process, generated and managed using the `.specify` framework. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementar um agente em `agente_reflexao_web` que combina busca web, reflexão guiada e memória para responder “Como funciona o Google Agent Development Kit?”. O fluxo seguirá o padrão LangGraph com geração inicial, até três reflexões fundamentadas pelas evidências Tavily e consolidação final em português com citações numeradas, inspirado nos agentes `agente_web`, `agente_reflexao_basica` e `agente_memoria`.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12.3  
**Primary Dependencies**: langgraph, langchain-core, langchain-google-genai, langchain-tavily, python-dotenv  
**Storage**: InMemorySaver (memória em execução; sem persistência em disco)  
**Testing**: Execução manual via `python agente_reflexao_web/main.py` (sem suites automatizadas)  
**Target Platform**: Script CLI Python em ambiente Linux com internet  
**Project Type**: Agente single-run orientado a console  
**Performance Goals**: Entregar resposta com fontes em <=3 iterações de reflexão e tempo de execução interativo (<60s)  
**Constraints**: Limite rígido de 3 reflexões, resposta em português, nenhuma flag/parâmetro extra, sem loops interativos contínuos, `.env` copiado de `agente_web` sem alterações  
**Scale/Scope**: Uma pergunta fixa por execução (Google Agent Development Kit)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Gate 1 (Principle IV)**: Confirmado uso do modelo `gemini-2.5-flash` em todos os nós → **PASS**  
- **Gate 2 (Principle V)**: Fluxo será implementado com LangGraph `StateGraph` e checkpoints → **PASS**  
- **Gate 3 (Principle I)**: `agente_reflexao_web/main.py` servirá como ponto de entrada e teste manual → **PASS**  
- **Gate 4 (Principle III)**: Sem criação de testes automatizados para componentes não determinísticos → **PASS**

*Revalidação pós-Fase 1*: Planejamento mantém conformidade com todas as regras constitucionais listadas acima.

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

**Structure Decision**: Criar `agente_reflexao_web/` replicando o padrão dos demais agentes (main script, pacote Python, README opcional e `.env` copiado de `agente_web`). O novo agente reutilizará estratégias de busca (`agente_web`), reflexão (`agente_reflexao_basica`) e memória (`agente_memoria`) sem alterar outros diretórios existentes.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
