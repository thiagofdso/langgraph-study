# Research for Router Persona Agent

## Langgraph Router Agents and Global Memory

### Router Agents
LangGraph implements router agents as a type of workflow that directs inputs to context-specific tasks based on their content. This is achieved by defining nodes for each potential path (e.g., persona agents) and using conditional edges to route the flow based on specific criteria (e.g., user age).

### Global Memory / Memory per `thread_id`
LangGraph handles memory through "checkpointers," which save the graph's state at each "super-step" to a "thread." A "thread" is a unique identifier for a sequence of runs, accumulating state over time. Checkpoints allow retrieval of the latest state, history, replaying, and state updates. For cross-thread memory, a "Store" interface can be used. Common checkpointer implementations include `InMemorySaver`, `SqliteSaver`, and `PostgresSaver`. The `InMemorySaver` is suitable for in-memory state management as requested.

### Durable Execution
Durable execution ensures workflows can pause and resume. This requires persistence with a checkpointer, a thread ID, and non-deterministic operations wrapped in `@task` to prevent re-execution upon resumption.

## Conclusion for Implementation Plan

-   **Primary Dependencies**: The existing `langgraph` dependency is sufficient for core routing and memory concepts. `langchain-core` and `langchain-community` are generally useful for LangChain integrations.
-   **Constraints**: The router agent will be implemented using conditional edges based on user age. Global memory per `thread_id` will be managed by configuring the Langgraph graph with an `InMemorySaver` checkpointer and passing a unique `thread_id` for each conversation.