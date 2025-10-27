# Quickstart: Simple Hello Agent

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

3.  **Create a `.env` file** in the `agente_simples` directory with the following content:
    ```
    GEMINI_API_KEY="YOUR_API_KEY"
    ```
    Replace `"YOUR_API_KEY"` with your actual Gemini API key.

## Running the Agent

To run the agent, execute the following command from the root directory:

```bash
python agente_simples/main.py
```

The agent will then prompt you to ask a question. Ask "quantos estados tem o brasil?" and the agent will respond.
