# langgraph Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-27

## Active Technologies
- Python 3.11 + `langgraph`, `google-generativeai`, `python-dotenv`, `langchain-google-genai` (002-memory-agent)
- `langgraph` for in-memory state management (for this simple case) (002-memory-agent)
- Python 3.11 + `langgraph`, `google-generativeai`, `python-dotenv`, `langchain-google-genai`, `langchain` (for tools) (003-calculator-agent)
- N/A (in-memory state for sequential agents) (004-sequential-persona-agent)
- Python 3.11 + `langgraph`, `google-generativeai`, `python-dotenv`, `langchain-google-genai`, `langchain` (for tools), `mcp-langgraph` (from the provided project) (005-mcp-agent)
- N/A (in-memory state for agents) (005-mcp-agent)
- Python 3.11 + langgraph, google-generativeai, python-dotenv, langchain-google-genai, langchain (for tools), mcp-langgraph (005-mcp-agent)
- Python 3.11 + langgraph, google-generativeai, python-dotenv, langchain-google-genai, langchain, langchain-core, langchain-community (Langgraph handles router agents via conditional edges and global memory via checkpointers like InMemorySaver, which is part of langgraph. No additional core dependencies are immediately required for these functionalities.) (001-router-persona-agent)
- In-memory state management for Langgraph (001-router-persona-agent)
- Python 3.11 + `langgraph`, `google-generativeai`, `python-dotenv`, `langchain-google-genai` (001-multimodal-mindmap-agent)
- Python 3.11 + `langgraph`, `google-generativeai`, `python-dotenv`, `langchain-google-genai`, `base64` (built-in Python library for PDF to base64 conversion). (006-pdf-analyzer-agent)
- In-memory state management (for this simple agent). (006-pdf-analyzer-agent)
- N/A (in-memory state) 007-multi-agent-parallel-content
- Python 3.11 + `docling`, `langgraph` (009-pdf-to-md-converter)
- Filesystem (009-pdf-to-md-converter)

- Python 3.11 + `langgraph`, `google-generativeai`, `python-dotenv` (001-simple-hello-agent)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11: Follow standard conventions

## Recent Changes
- 009-pdf-to-md-converter: Added Python 3.11 + `docling`, `langgraph`
- 008-multi-agent-orchestration-report: Added Python 3.11 + langgraph, google-generativeai, python-dotenv, langchain-google-genai, langchain
- 001-multi-agent-parallel-content: Added Python 3.11 + langgraph, google-generativeai, python-dotenv, langchain-google-genai, langchain


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
