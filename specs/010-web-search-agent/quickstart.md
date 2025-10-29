# Quickstart — Web Search Agent Summary

## Prerequisites
- Python 3.12 with the repository virtual environment activated (`source venv/bin/activate`).
- Active API keys for Google Gemini (`GEMINI_API_KEY`) and Tavily (`TAVILY_API_KEY`).
- Internet connectivity allowed from the execution environment.

## Setup Steps
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Ensure `langchain-tavily` is present; add it to `requirements.txt` if missing before installing.

2. **Configure environment variables**
   - Copy `.env` from `agente_simples` to the repository root (as required by the constitution).
   - Update the new `.env` with:
     ```
     GEMINI_API_KEY="your-gemini-key"
     TAVILY_API_KEY="your-tavily-key"
     ```
   - Additional settings (e.g., default temperature) can be appended later if needed.

3. **Create project folder structure**
   - Ensure the following files exist under `agente_web/`:
     - `__init__.py`
     - `main.py`
     - `graph.py`
     - `tools.py`
     - `summarizer.py`
     - `prompts.py`

## Running the Agent
Run the entry point from the repository root:
```bash
python agente_web/main.py
```
`main.py` will prompt for a question; choose to enter a custom prompt or trigger the built-in smoke-test flow for "Como pesquisar arquivos no linux?" without supplying command-line arguments.

## Manual Verification Checklist
- [ ] Question shorter than five characters triggers a validation warning.
- [ ] Normal questions return at least three Tavily results when available.
- [ ] Summaries cite two or more distinct sources in the response body.
- [ ] Smoke-test command completes in under 10 seconds under typical network conditions.
