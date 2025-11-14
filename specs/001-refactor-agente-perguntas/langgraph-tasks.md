# Documento de Tarefa: Reestruturar Agente Perguntas

## 1. Análise Atual
### 1.1 Estado Atual
- Estrutura mínima: pacote `agente_perguntas/` contém `main.py` monolítico, `prompt.py`, `README.md` e apenas `__init__.py` vazio.
- A execução ocorre via `python agente_perguntas/main.py`, sem suporte a `python -m agente_perguntas`.
- Não há separação clara de responsabilidades: lógica do LangGraph, configuração, estado tipado, logging e CLI estão misturados no `main.py`.
- Ausência de `.env.example`, diretório de testes, documentação operacional e logs estruturados.
- Interação humana (interrupt) é implementada diretamente dentro do fluxo, sem camada dedicada de utilidades ou validações.

### 1.2 Impacto da Mudança
- Refatoração quebrará o monólito em módulos (config, state, graph, cli, utils) alinhados ao padrão `agente_simples`.
- Necessário atualizar pontos de entrada (`__main__.py` e CLI) para manter compatibilidade com execução interativa.
- Introdução de testes automatizados, arquivos de configuração e documentação exigirá ajustes em pipelines de build/tests.
- Logs estruturados e validação de configuração impactam observabilidade e DX; garantir que mensagens sigam idioma/PT-BR.

## 2. Requisitos & Objetivos
### 2.1 Objetivo Principal
Reorganizar `agente_perguntas` para seguir boas práticas de projetos LangGraph (estrutura modular, configuração centralizada, testes e documentação), mantendo a execução local com interação humana via `python -m agente_perguntas`.

### 2.2 Escolha de API
Manter **Graph API (StateGraph)** já utilizada implicitamente, pois o fluxo envolve checkpointing simples, interrupt humano e estado compartilhado. Functional API não adiciona benefícios aqui.

### 2.3 Estrutura do Projeto
Adotar a **estrutura básica single-agent** usada em `agente_simples`, adaptando nomes:
```
agente_perguntas/
├── __init__.py
├── __main__.py
├── cli.py
├── config.py
├── graph.py
├── state.py
├── utils/
│   ├── __init__.py
│   ├── logging.py
│   ├── nodes.py
│   ├── prompts.py
│   └── similarity.py
├── docs/
│   └── operations.md
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_graph.py
│   └── test_similarity.py
└── logs/ (criado em runtime)
```

## 3. Organização de Arquivos
### 3.1 Estrutura Base
- Migrar `main.py` para `cli.py` e `__main__.py` (ponto de entrada).
- Extrair lógica de configuração e constantes para `config.py`.
- Criar `state.py` com `TypedDict` (ou `pydantic.BaseModel` se validação extra for necessária) descrevendo o estado de interação.
- Mover funções de prompt/FAQ para `utils/prompts.py` e separar utilitário de similaridade em `utils/similarity.py`.
- Centralizar nós do grafo (inclusive HITL) em `utils/nodes.py`.
- Configurar logging estruturado em `utils/logging.py`.

### 3.2 Padrões de Importação
- Usar a convenção Stdlib → Third-party → Local, com blocos separados por linha em branco.
- Evitar `from module import *`. Tornar exportações explícitas no `utils/__init__.py`.

## 4. Implementação Detalhada

### 4.1 State & Config
1. **Criar `agente_perguntas/config.py`** consolidando variáveis:
```python
"""Centralização de configuração para o agente de perguntas."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

DEFAULT_LOG_DIR = Path(os.getenv("AGENTE_PERGUNTAS_LOG_DIR", "agente_perguntas/logs"))

@dataclass(frozen=True)
class AppConfig:
    gemini_api_key: str
    model_name: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
    confidence_threshold: float = float(os.getenv("AGENTE_PERGUNTAS_CONFIDENCE", "0.7"))
    log_dir: Path = DEFAULT_LOG_DIR

    @classmethod
    def load(cls) -> "AppConfig":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY não configurado. Consulte README.")
        return cls(gemini_api_key=api_key)
```
2. **Criar `agente_perguntas/state.py`** com estado tipado:
```python
from __future__ import annotations

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict, total=False):
    question: str
    answer: str
    confidence: float
    status: str
    notes: str
    messages: Annotated[list[dict], add_messages]
```
3. Atualizar nós para consumir `AppConfig` (injeção via função ou closure).

### 4.2 Nodes, Prompt & Similarity
1. **`utils/prompts.py`** deve expor `DEMO_QUESTIONS`, `get_faq_entries`, `build_system_prompt` (sem side effects). Adicionar docstring com referência ao spec.
2. **`utils/similarity.py`** para encapsular `score_similarity` e `rank_faq_by_similarity` com testes de unidade.
3. **`utils/nodes.py`**: separar `_evaluate_question`, `_resume_interrupt` e `run_demo` do spec em funções puras, recebendo dependências (config, logger, prompt helpers). Example:
```python
from langgraph.types import Command, interrupt

def evaluate_question(state: AgentState, helpers: SimilarityHelpers, cfg: AppConfig) -> AgentState:
    question = state.get("question", "").strip()
    ranked = helpers.rank(question)
    best_entry, score = ranked[0]

    if score >= cfg.confidence_threshold:
        return {
            "answer": best_entry["answer"],
            "confidence": score,
            "status": "respondido automaticamente",
            "notes": f"Correspondência: {best_entry['question']}"
        }

    payload = helpers.build_interrupt_payload(question, ranked)
    human_data = interrupt(payload)
    return {
        "answer": human_data.get("message", helpers.default_escalation_message),
        "confidence": score,
        "status": "encaminhar para humano",
        "notes": human_data.get("notes", "Aguardando atendimento humano."),
    }
```
4. Expor funções públicas em `utils/__init__.py` para facilitar import nos testes.

### 4.3 Graph Construction (`graph.py`)
1. Criar `build_graph(config: AppConfig) -> Graph` semelhante a `agente_simples.graph`:
```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from agente_perguntas.state import AgentState
from agente_perguntas.utils.nodes import evaluate_question


def build_graph(config: AppConfig):
    builder = StateGraph(AgentState)
    builder.add_node("evaluate", lambda state: evaluate_question(state, config))
    builder.add_edge(START, "evaluate")
    builder.add_edge("evaluate", END)
    return builder.compile(checkpointer=InMemorySaver())

GRAPH = build_graph(AppConfig.load())
```
2. Permitir injeção de checkpointer externo para futuros ambientes (factory).
3. Garantir que o interrupt continue funcionando após a refatoração (escrever teste dedicado).

### 4.4 CLI & Execução (`cli.py` / `__main__.py`)
1. Reescrever CLI inspirado em `agente_simples/cli.py`, mantendo modo demo e pergunta única:
```python
import argparse

from agente_perguntas.config import AppConfig
from agente_perguntas.graph import build_graph
from agente_perguntas.utils.logging import setup_logging
from agente_perguntas.utils.prompts import DEMO_QUESTIONS
from agente_perguntas.utils.runner import run_question, run_demo


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser("agente_perguntas")
    parser.add_argument("--pergunta", help="Pergunta única a ser respondida")
    args = parser.parse_args(argv)

    config = AppConfig.load()
    logger = setup_logging(config.log_dir)
    graph = build_graph(config)

    if args.pergunta:
        run_question(graph, args.pergunta, logger=logger)
    else:
        run_demo(graph, DEMO_QUESTIONS, logger=logger)

    return 0
```
2. Criar `__main__.py` com:
```python
from agente_perguntas.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```
3. Garantir que `python -m agente_perguntas` siga exibindo prompts de interação humana quando necessário.

### 4.5 Logging & Observabilidade
1. Implementar `utils/logging.py` similar ao `agente_simples`:
   - Configurar `logging.getLogger(__name__)` com `structlog` ou formato JSON simples.
   - Criar diretório de logs se não existir.
2. No CLI, logar início/fim de execução, perguntas processadas, status final e notas.
3. Preparar hook para futura integração com LangSmith (comentário TODO).

### 4.6 Documentação & Configuração
1. Atualizar `README.md` com passos: ativar venv, copiar `.env.example`, executar `python -m agente_perguntas` e interpretar logs.
2. Criar `.env.example` com variáveis `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_TEMPERATURE`, `AGENTE_PERGUNTAS_CONFIDENCE`, `AGENTE_PERGUNTAS_LOG_DIR`.
3. Criar `docs/operations.md` cobrindo:
   - Fluxo de escalonamento humano
   - Como atualizar FAQ e rodar testes
   - Troubleshooting para erros de configuração/modelo

## 5. Testing Strategy
### 5.1 Unit Tests
- `tests/test_similarity.py`: cobrir `score_similarity`, `rank_faq_by_similarity` (casos com stopwords, perguntas vazias, empates).
- `tests/test_nodes.py` (opcional, pode ser incorporado a `test_graph`): garantir que `evaluate_question` retorne status correto com diferentes scores.
- Mockar `interrupt` para validar fluxo HITL sem input real.

### 5.2 Integration Tests
- `tests/test_graph.py`: simular perguntas com e sem correspondência; usar `graph.invoke` e checar estado final.
- `tests/test_cli.py`: usar `subprocess` ou `CliRunner` para validar saída do CLI nos modos demo e pergunta única (mock de `input`).
- Garantir que logs sejam criados (pode usar diretório temporário via `tmp_path`).

### 5.3 Manual QA
- Checklist curto no README para validar: execução demo, pergunta desconhecida, ausência de `GEMINI_API_KEY`, criação de log, execução do teste `pytest agente_perguntas/tests -v`.

## 6. Deployment & Monitoring
### 6.1 Estrutura Final
- Confirmar que `langgraph.json` ou equivalente (se adotado futuramente) aponta para `agente_perguntas/graph.py:build_graph`.
- Garantir que `Makefile` (caso exista) tenha alvos `test` e `run-agente-perguntas`.

### 6.2 Checklist Final
- [ ] Estrutura modular criada conforme diagrama.
- [ ] `.env.example` e README atualizados.
- [ ] Logs estruturados funcionando (arquivo criado após execução).
- [ ] CLI suportando `python -m agente_perguntas` com HITL.
- [ ] Suíte `pytest agente_perguntas/tests -v` passando.
- [ ] Documentação operacional disponível em `docs/operations.md`.
- [ ] Validação manual concluída (demo + pergunta avulsa + falta de API key).
