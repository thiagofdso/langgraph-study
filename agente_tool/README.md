# Quickstart: Calculator Agent

## Setup

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file** in the `agente_tool` directory with the following content:
    ```
    GEMINI_API_KEY="YOUR_API_KEY"
    ```
    Replace `"YOUR_API_KEY"` with your actual Gemini API key.

## Running the Agent

To run the agent, execute the following command from the root directory:

```bash
python agente_tool/main.py
```

The agent will then prompt you to ask a question. Ask "quanto é 300 dividido por 4?" and the agent should use its calculator tool to respond with "75".
