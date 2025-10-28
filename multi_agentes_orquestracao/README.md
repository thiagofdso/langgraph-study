# Multi-Agent Orchestration for Report Generation

This project implements a multi-agent system using `langgraph` to orchestrate the generation of comprehensive reports. An orchestrator agent plans the report and dynamically determines sections, worker agents generate text for these sections in parallel, and a synthesizer consolidates the sections into a final report.

## Feature Description

The system operates as follows:
-   **Orchestrator**: Receives a theme, generates a plan for the report, and dynamically determines the sections (subtasks) based on the theme.
-   **Workers**: Each worker agent receives a section and generates its text content in parallel.
-   **Orchestrator/Synthesizer**: Consolidates all the sections written by the worker agents into a final, coherent report.

## Technologies Used

-   Python 3.11
-   `langgraph` for agent orchestration
-   `google-generativeai` for LLM interaction
-   `python-dotenv` for environment variable management
-   `langchain-google-genai` and `langchain` for LLM integration
-   `pydantic` for structured output from LLMs

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
    This will run the Langgraph workflow, generating a report based on the default topic "Inteligência Artificial" and printing the final report.

## Example Output

```
[Generated Report with multiple sections]
```
