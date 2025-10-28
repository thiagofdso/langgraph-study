# Quickstart: Multi-Agent Parallel Content Generation

This guide provides instructions to quickly set up and run the Multi-Agent Parallel Content Generation system.

## Prerequisites

-   Python 3.11 installed.
-   `venv` for virtual environment management.
-   Google API Key with access to `gemini-2.5-flash`.

## Setup

1.  **Navigate to the project directory**:
    ```bash
    cd /root/code/langgraph/multi_agentes_paralelo/agente_paralelo
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
    *(Note: `requirements.txt` will be created during implementation phase)*

4.  **Configure environment variables**:
    Copy the `.env` file from `agente_simples` and populate it with your Google API Key.
    ```bash
    cp ../../agente_simples/.env .env
    # Open .env and add/update your GOOGLE_API_KEY
    ```

## Running the System

1.  **Execute the main script**:
    ```bash
    python main.py
    ```
    This will run the Langgraph workflow, generating a joke, story, and poem based on the fixed topic "gatos" and printing the combined output.

## Example Output

```
Aqui está uma história, piada e poema sobre gatos!

HISTÓRIA:
[Generated story about cats]

PIADA:
[Generated joke about cats]

POEMA:
[Generated poem about cats]
```
