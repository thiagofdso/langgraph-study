# Multimodal Mindmap Agent

This project implements a multimodal agent that analyzes a mind map image (`folder_map.png`) and generates a hierarchical markdown output. The refactor aligns its layout with other LangGraph agents, separating configuration, state, nodes, workflow assembly, CLI, and tests.

## Quickstart

This document provides a quick guide to setting up and running the Multimodal Mindmap Agent.

### Prerequisites

- Python 3.11
- `venv` for virtual environment management
- Dependencies listed in `requirements.txt`

### Setup

1.  **Clone the repository** (if you haven't already):

    ```bash
    git clone <repository_url>
    cd langgraph
    ```

2.  **Create and activate a virtual environment**:

    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Prepare the input image**:

    Place your mind map image named `folder_map.png` in the project root directory.

## Project Structure

```text
agente_imagem/
├── __init__.py
├── __main__.py
├── cli.py
├── config.py
├── graph.py
├── main.py
├── state.py
└── utils/
    ├── __init__.py
    ├── io.py
    ├── logging.py
    └── nodes.py
```

- `config.py`: carrega credenciais e expõe `AppConfig`.
- `state.py`: define o `GraphState` compartilhado e constantes de status.
- `utils/io.py`: funções de leitura, criação e validação de imagens.
- `utils/nodes.py`: nós do LangGraph responsáveis por validação, preparo, invocação e formatação.
- `utils/logging.py`: fornece `get_logger` para logs consistentes.
- `graph.py`: (fase seguinte) reunirá o workflow compilado com `create_app()`.
- `cli.py`: (fase seguinte) entregará o CLI alinhado ao LangGraph.

### Running the Agent (legacy script)

The refactor preservers the legacy script for backward compatibility. To process `folder_map.png` using the new modularized nodes:

```bash
python agente_imagem/main.py
```

When executed with a valid `GOOGLE_API_KEY`, the agent prints the hierarchical markdown representation of the mind map. If the image is unclear, unreadable, or not a mind map, the agent logs the issue and terminates without returning markdown. The CLI and LangGraph integration will be documented after their dedicated tasks complete.
