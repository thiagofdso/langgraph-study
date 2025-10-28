# Quickstart: Sequential Persona Generation Agent

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

3.  **Create a `.env` file** in the `multi_agentes_sequencial` directory with the following content:
    ```
    GEMINI_API_KEY="YOUR_API_KEY"
    ```
    Replace `"YOUR_API_KEY"` with your actual Gemini API key.

## Running the Agent

To run the multi-agent system, execute the following command from the root directory:

```bash
python multi_agentes_sequencial/main.py
```

The system will then generate a random persona and format it into a JSON structure, which will be printed to the console.
