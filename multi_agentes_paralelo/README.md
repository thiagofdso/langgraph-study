# Multi-Agent Parallel Content Generation

This project implements a multi-agent system using `langgraph` to generate creative content (joke, story, and poem) in parallel based on a given topic, and then aggregates the results into a single output.

## Feature Description

The system receives a topic (e.g., "gatos") and dispatches three agents in parallel:
-   **Agent 1**: Generates a joke about the topic.
-   **Agent 2**: Generates a story about the topic.
-   **Agent 3**: Generates a poem about the topic.

After all three agents complete their tasks, an aggregator combines all the results into a single, unified output.

## Technologies Used

-   Python 3.11
-   `langgraph` for agent orchestration
-   `google-generativeai` for LLM interaction
-   `python-dotenv` for environment variable management
-   `langchain-google-genai` and `langchain` for LLM integration

## Setup

1.  **Navigate to the project directory**:
    ```bash
    cd multi_agentes_paralelo
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
    Copy the `.env` file from `agente_simples` (located at the project root) to the `multi_agentes_paralelo` directory and populate it with your Google API Key.
    ```bash
    cp ../agente_simples/.env .env
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
