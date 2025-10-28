# Multimodal Mindmap Agent

This project implements a multimodal agent that analyzes a mind map image (`folder_map.png`) and generates a hierarchical markdown output.

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

### Running the Agent

To run the agent and process the `folder_map.png` image, execute the `main.py` script within the `agente_imagem` directory:

```bash
python agente_imagem/main.py
```

The agent will analyze the `folder_map.png` and print the hierarchical markdown representation of the mind map to the console.

### Expected Output

The output will be a markdown string representing the hierarchical structure of the mind map, including node text and hierarchical level. If the image is unclear, unreadable, or not a mind map, the agent will log the issue and terminate without returning any output.
