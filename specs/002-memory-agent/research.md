# Research: Memory Agent Implementation

## Decision

Leverage `langgraph`'s built-in memory management capabilities, specifically by utilizing `StateGraph` to define and manage the conversational state, which inherently supports memory per thread (or per invocation in a stateless context).

## Rationale

The `agente_simples` project already uses `langgraph`'s `StateGraph` for defining the agent's workflow. `StateGraph` is designed to manage state transitions, making it suitable for implementing conversational memory. By defining a `GraphState` that includes the conversation history, the agent can access and update its memory across turns. This approach aligns with the existing `agente_simples` structure and `langgraph` best practices.

## Alternatives Considered

-   **Manual memory management**: Storing conversation history in a simple list or database. This would require more boilerplate code and would not leverage `langgraph`'s state management features effectively.
-   **External memory stores**: Using a dedicated memory store like Redis or a database. While suitable for more complex, persistent memory requirements, for this simple agent, `langgraph`'s in-memory state is sufficient and simpler to implement.
