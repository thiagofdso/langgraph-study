# LangGraph Task Plan: Refactor agente_imagem Structure

## 1. Panorama Atual
- `agente_imagem` concentra toda a lógica em `main.py`, com utilitários de imagem em `utils.py` e sem módulos dedicados a `state`, `config`, `graph` ou CLI.
- O fluxo atual possui nodes `validate_and_encode`, `invoke_llm` e `parse_llm_response`, compilados em `workflow = StateGraph(AgentState)` e invocados diretamente via script.
- Logs usam `logging.basicConfig` em `main.py`, o que conflita com o padrão centralizado usado em `agente_simples` (`utils/logging.py`).
- Variáveis de ambiente são carregadas com `load_dotenv()` e `GOOGLE_API_KEY`, diferente dos demais agentes que centralizam configurações em `config.py`.

## 2. Objetivo de Refatoração
- Reorganizar `agente_imagem` para seguir a estrutura modular de `agente_simples`, preservando comportamento (mesmo markdown, mesmos logs e fallback de imagem).
- Expor `create_app()` e `app` para compatibilidade com LangGraph CLI e `langgraph.json`.
- Aderir aos padrões de nomenclatura de nodes descritos em `graph-nodes-patterns.md` (`validate_input`, `invoke_model`, `format_response`) e acrescentar nomes consistentes para etapas adicionais (e.g. `prepare_image`).

## 3. Conjunto de Tarefas

### T1 — Congelar comportamento atual para comparação
- Executar o script atual com a imagem padrão para registrar markdown, logs e situações de erro (imagem inválida e falta de API key).
- Guardar os artefatos (texto ou fixtures) para comparação durante testes pós-refatoração.

```bash
poetry run python agente_imagem/main.py > artefatos/baseline_output.txt
poetry run python agente_imagem/main.py --imagem inexistente.png 2> artefatos/baseline_error.log
```

### T2 — Criar esqueleto de diretórios e arquivos
- Replicar a estrutura de `agente_simples` criando módulos vazios: `config.py`, `state.py`, `graph.py`, `cli.py`, `__main__.py`, `utils/__init__.py`, `utils/nodes.py`, `utils/io.py` (para funções de arquivo/imagem) e `tests/test_agente_imagem.py`.
- Ajustar `__init__.py` para expor futuras fábricas.

```bash
mkdir -p agente_imagem/utils tests
cat <<'PY' > agente_imagem/utils/__init__.py
"""Utility exports for agente_imagem."""

from .io import image_to_base64
from .nodes import (
    validate_input_node,
    prepare_image_node,
    invoke_model_node,
    format_response_node,
)

__all__ = [
    "image_to_base64",
    "validate_input_node",
    "prepare_image_node",
    "invoke_model_node",
    "format_response_node",
]
PY
```

### T3 — Centralizar configuração em `config.py`
- Mover `load_dotenv()` e leitura de `GOOGLE_API_KEY` para uma dataclass semelhante a `AppConfig` de `agente_simples`.
- Garantir mensagem de erro equivalente à atual quando a chave estiver ausente.

```python
# agente_imagem/config.py
from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class AppConfig:
    model_name: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    api_key: str | None = os.getenv("GOOGLE_API_KEY")
    temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.0"))

    def require_api_key(self) -> str:
        if not self.api_key:
            raise RuntimeError("GOOGLE_API_KEY não configurada. Consulte README.")
        return self.api_key

config = AppConfig()
```

### T4 — Definir estado compartilhado em `state.py`
- Reescrever o `TypedDict` atual (`AgentState`) como `GraphState` seguindo formato de `agente_simples`, incluindo campos para imagem base64, resposta do LLM e markdown.
- Adicionar constantes de status reutilizáveis.

```python
# agente_imagem/state.py
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class GraphState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    image_path: str
    image_bytes: bytes
    base64_image: str
    llm_response: str
    markdown_output: str
    status: str

STATUS_VALIDATED = "validated"
STATUS_INVOKED = "invoked"
STATUS_FORMATTED = "formatted"
STATUS_ERROR = "error"
```

### T5 — Reorganizar utilitários de imagem em `utils/io.py`
- Migrar `image_to_base64` e `base64_to_image` para `utils/io.py`, adicionando tratamento de exceções alinhado aos logs atuais.

```python
# agente_imagem/utils/io.py
import base64
from pathlib import Path
from PIL import Image

class ImageLoadError(RuntimeError):
    pass

def image_to_base64(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise ImageLoadError(f"Arquivo não encontrado: {file_path}")
    with file_path.open("rb") as handle:
        return base64.b64encode(handle.read()).decode("utf-8")

def ensure_sample_image(default_path: Path) -> None:
    if default_path.exists():
        return
    Image.new("RGB", (60, 30), color="red").save(default_path)
```

### T6 — Implementar nodes seguindo `graph-nodes-patterns.md`
- Renomear responsabilidades para aderir aos padrões: `validate_input`, `prepare_image`, `invoke_model`, `format_response`.
- `validate_input_node` deve validar caminho, criar metadata e acionar `ensure_sample_image` quando necessário.
- `prepare_image_node` encapsula a lógica de leitura/verificação com `PIL.Image.verify()` e converte para base64.
- `invoke_model_node` usa `ChatGoogleGenerativeAI` instanciado via `config.require_api_key()` mantendo mensagens existentes.
- `format_response_node` preserva tratamento de `INVALID_IMAGE` e retorna markdown.

```python
# agente_imagem/utils/nodes.py
from langchain_core.messages import HumanMessage
from agente_imagem.config import config
from agente_imagem.state import (
    GraphState,
    STATUS_ERROR,
    STATUS_FORMATTED,
    STATUS_INVOKED,
    STATUS_VALIDATED,
)
from agente_imagem.utils.io import image_to_base64, ensure_sample_image, ImageLoadError

DEFAULT_IMAGE = "folder_map.png"

def validate_input_node(state: GraphState) -> GraphState:
    image_path = state.get("image_path") or DEFAULT_IMAGE
    ensure_sample_image(Path(image_path))
    return {
        "image_path": image_path,
        "status": STATUS_VALIDATED,
        "messages": state.get("messages", []),
    }

def prepare_image_node(state: GraphState) -> GraphState:
    try:
        encoded = image_to_base64(state["image_path"])
    except ImageLoadError as exc:
        return {"status": STATUS_ERROR, "markdown_output": None, "error": str(exc)}
    return {"base64_image": encoded}

def invoke_model_node(state: GraphState) -> GraphState:
    llm = ChatGoogleGenerativeAI(model=config.model_name, google_api_key=config.require_api_key())
    message = HumanMessage([...])
    response = llm.invoke([message])
    return {"llm_response": response.content, "status": STATUS_INVOKED}

def format_response_node(state: GraphState) -> GraphState:
    content = state.get("llm_response")
    if not content or "INVALID_IMAGE" in content:
        return {"status": STATUS_ERROR, "markdown_output": None}
    return {"markdown_output": content, "status": STATUS_FORMATTED}
```

### T7 — Construir `graph.py` com fábrica `create_app()`
- Declarar builder `StateGraph(GraphState)` adicionando nodes com os nomes padronizados e edges lineares.
- Compilar o grafo e expor `app` (compatível com `agente_simples`).

```python
# agente_imagem/graph.py
from langgraph.graph import StateGraph, START, END
from agente_imagem.state import GraphState
from agente_imagem.utils.nodes import (
    validate_input_node,
    prepare_image_node,
    invoke_model_node,
    format_response_node,
)

def create_app():
    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_input_node)
    builder.add_node("prepare_image", prepare_image_node)
    builder.add_node("invoke_model", invoke_model_node)
    builder.add_node("format_response", format_response_node)
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "prepare_image")
    builder.add_edge("prepare_image", "invoke_model")
    builder.add_edge("invoke_model", "format_response")
    builder.add_edge("format_response", END)
    return builder.compile()

app = create_app()
```

### T8 — CLI alinhada ao padrão de `agente_simples`
- Implementar `cli.py` com pré-checagens (`config.require_api_key`), prompts de entrada e logging consistente.
- Permitir passagem opcional de caminho de imagem via `--image`.

```python
# agente_imagem/cli.py
import argparse
from agente_imagem.config import config
from agente_imagem.graph import app

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default="folder_map.png")
    args = parser.parse_args()

    config.require_api_key()
    result = app.invoke({"image_path": args.image})
    markdown = result.get("markdown_output") or "Falha ao gerar markdown."
    print(markdown)

if __name__ == "__main__":
    main()
```

### T9 — Simplificar `main.py` para delegar à CLI
- Reduzir `main.py` para atuar como wrapper (`from .cli import main`), mantendo compatibilidade com scripts existentes.

```python
# agente_imagem/main.py
from agente_imagem.cli import main

if __name__ == "__main__":
    main()
```

### T10 — Expor fábrica no pacote
- Atualizar `agente_imagem/__init__.py` para exportar `create_app` e `app`.

```python
# agente_imagem/__init__.py
from agente_imagem.graph import app, create_app

__all__ = ["app", "create_app"]
```

### T11 — Atualizar `langgraph.json`
- Incluir a nova entrada `"agente-imagem": "agente_imagem/graph.py:create_app"` garantindo execução via CLI.

```json
{
  "graphs": {
    "agente-simples": "agente_simples/graph.py:create_app",
    "agente-imagem": "agente_imagem/graph.py:create_app"
  }
}
```

### T12 — Migrar logging para utilitário compartilhado
- Criar `agente_imagem/utils/logging.py` inspirado em `agente_simples/utils/logging.py`.
- Substituir `logging.basicConfig` por uso do logger local (`get_logger(__name__)`).

```python
# agente_imagem/utils/logging.py
import logging

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
```

### T13 — Testes automatizados de regressão
- Criar `tests/test_agente_imagem.py` com fixtures para imagem de sucesso e cenário inválido.
- Mockar `ChatGoogleGenerativeAI.invoke` para garantir determinismo.

```python
# tests/test_agente_imagem.py
from unittest.mock import patch
from agente_imagem.graph import app

@patch("agente_imagem.utils.nodes.ChatGoogleGenerativeAI")
def test_success_path(mock_llm, tmp_path):
    mock_llm.return_value.invoke.return_value.content = "# Heading\n- Item"
    result = app.invoke({"image_path": "folder_map.png"})
    assert result["markdown_output"].startswith("# Heading")

@patch("agente_imagem.utils.nodes.ChatGoogleGenerativeAI")
def test_missing_image(mock_llm):
    result = app.invoke({"image_path": "nao_existe.png"})
    assert result["status"] == "error"
```

### T14 — Atualizar documentação e exemplos
- Revisar `agente_imagem/README.md` descrevendo novo comando (`python -m agente_imagem.cli --image caminho.png`) e requisitos (`GOOGLE_API_KEY`).
- Incluir sessão sobre uso via LangGraph CLI (`langgraph run agente-imagem --input '{"image_path": "folder_map.png"}'`).

```markdown
```bash
langgraph run agente-imagem --input '{"image_path": "folder_map.png"}'
```
```

### T15 — Garantir compatibilidade para resets e fallback
- Escrever tarefa de verificação para que `prepare_image_node` mantenha criação de imagem dummy quando arquivo não existir (comportamento atual de `main.py`).
- Documentar decisão nas docstrings e nos testes.

```python
# Dentro de prepare_image_node
if not Path(image_path).exists():
    ensure_sample_image(Path(image_path))
```

### T16 — Checklist final de revisão
- Concluir refatoração apenas após rodar `pytest -k agente_imagem`, executar CLI e validar logs/outputs idênticos aos artefatos de T1.
- Revisar cobertura (`pytest --maxfail=1 --disable-warnings -q`).

```bash
pytest -k agente_imagem -q
python -m agente_imagem.cli --image folder_map.png
```

