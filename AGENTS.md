# langgraph Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-29

## Active Technologies
- Python 3.12.3 (repo virtualenv) + langgraph, langchain-core, sqlite3 (stdlib), tabulate/markdown handling TBD (likely use `textwrap` or manual formatting) (011-sqlite-sales-agent)
- Local SQLite database file within `agente_banco_dados` (011-sqlite-sales-agent)
- Python 3.12.3 (repo virtualenv) + langgraph, langchain-core, google-generativeai (Gemini), sqlite3 (stdlib not used here but available), textwrap/typing (stdlib) (012-faq-routing-agent)
- FAQ embedded directly in prompt text (no external storage); simple in-memory interaction log (012-faq-routing-agent)
- Python 3.12.3 + langgraph, langchain-core, google-generativeai (`gemini-2.5-flash`), python-dotenv (via project standard), standard library I/O utilities (013-task-agent)
- In-memory session state only (task list and completion markers) (013-task-agent)
- Python 3.12.3 + LangGraph, langchain-core, google-generativeai (`gemini-2.5-flash`), python-dotenv (014-add-reflection-agent)
- None (in-memory session state only) (014-add-reflection-agent)
- Sistema de arquivos local (artefatos de código e logs) (015-auto-code-agent)
- Python 3.12.3 + langgraph, langchain-core, langchain-google-genai, langchain-tavily, python-dotenv (016-add-reflexion-web)
- InMemorySaver (memória em execução; sem persistência em disco) (016-add-reflexion-web)

- Python 3.12.3 (repo virtualenv) + langgraph; langchain-core; google-generativeai; langchain-tavily (010-web-search-agent)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.12.3 (repo virtualenv): Follow standard conventions

## Recent Changes
- 016-add-reflexion-web: Added Python 3.12.3 + langgraph, langchain-core, langchain-google-genai, langchain-tavily, python-dotenv
- 015-auto-code-agent: Added Python 3.12.3 + LangGraph, langchain-core, google-generativeai (`gemini-2.5-flash`), python-dotenv
- 014-add-reflection-agent: Added Python 3.12.3 + LangGraph, langchain-core, google-generativeai (`gemini-2.5-flash`), python-dotenv


<!-- MANUAL ADDITIONS START -->
## CRITICAL: Use ripgrep, not grep

NEVER use grep for project-wide searches (slow, ignores .gitignore). ALWAYS use rg.

- `rg "pattern"` — search content
- `rg --files | rg "name"` — find files
- `rg -t python "def"` — language filters

## File finding

- Prefer `fd` (or `fdfind` on Debian/Ubuntu). Respects .gitignore.

## JSON

- Use `jq` for parsing and transformations.

## Agent Instructions

- Replace commands: grep→rg, find→rg --files/fd, ls -R→rg --files, cat|grep→rg pattern file
- Cap reads at 250 lines; prefer `rg -n -A 3 -B 3` for context
- Use `jq` for JSON instead of regex

<!-- MANUAL ADDITIONS END -->
