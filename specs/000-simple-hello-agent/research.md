# Research: Simple Hello Agent

## Decisions

*   **Framework**: `langgraph` will be used to build the agent's graph.
*   **LLM**: `gemini-2.5-flash` will be used for its speed and cost-effectiveness.
*   **Environment Variables**: `python-dotenv` will be used to manage the Gemini API key.

## Rationale

*   `langgraph` is a good choice for building stateful, multi-actor applications with LLMs. While this agent is simple, using `langgraph` from the start allows for future expansion.
*   `gemini-2.5-flash` is a fast and capable model suitable for this simple question-answering task.
*   `python-dotenv` is a standard and easy way to manage environment variables in Python projects.

## Alternatives Considered

*   **No framework**: For this simple agent, we could have written the logic without a framework. However, using `langgraph` provides a structure that is easier to maintain and extend.
*   **Other LLMs**: Other models could have been used, but `gemini-2.5-flash` meets the requirements of being fast and cost-effective.
