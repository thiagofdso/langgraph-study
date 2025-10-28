# Quickstart: Multi-Agent Orchestration for Report Generation

This guide provides instructions to quickly set up and run the Multi-Agent Orchestration system for report generation.

## Prerequisites

-   Python 3.11 installed.
-   `venv` for virtual environment management.
-   Google API Key with access to `gemini-2.5-flash`.

## Setup

1.  **Navigate to the project directory**:
    ```bash
    cd multi_agentes_orquestracao
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
    Copy the `.env` file from `agente_simples` (located at the project root) to the `multi_agentes_orquestracao` directory and populate it with your Google API Key.
    ```bash
    cp ../agente_simples/.env .env
    # Open .env and add/update your GOOGLE_API_KEY
    ```

## Running the System

1.  **Execute the main script**:
    ```bash
    python main.py
    ```
    This will run the Langgraph workflow, generating a report based on a default topic (e.g., "O que são agentes de ia?") and printing the final report.

## Example Output

```
[Generated Report]
```
