# Quickstart: SQLite Sales Agent

## Prerequisites
- Activate the repository virtual environment: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows).
- Copy `.env` from `agente_simples/.env` into `agente_banco_dados/.env` and adjust any project-specific variables if added later (none required initially).
- Ensure the `requirements.txt` dependencies are installed (`pip install -r requirements.txt`).

## Run the Agent
1. From the repo root, execute the agent entry point:
   ```bash
   python agente_banco_dados/main.py
   ```
2. The script will:
   - Initialize or reuse `agente_banco_dados/data/sales.db` by running `db_init.py` (idempotent seeding).
   - Build the LangGraph workflow and execute it once.
   - Display a markdown report in the terminal summarizing top products and sellers sourced from the local database.

## Resetting the Dataset (Optional)
- Delete the SQLite file (`rm agente_banco_dados/data/sales.db`) and rerun the agent to recreate seed data.
- To tweak the sample dataset, edit the constants in `db_init.py` and rerun the agent (changes take effect after deleting the existing DB).

## Troubleshooting
- If Python raises `sqlite3.OperationalError` about foreign keys, ensure the database file was recreated after enabling foreign key enforcement in `db_init.py`.
- If markdown tables look misaligned, confirm your terminal uses a monospace font or pipe the output to a markdown renderer.
