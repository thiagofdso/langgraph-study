# Research: LangGraph Multi-Agent Systems and Subgraphs

## Decision

Implement the sequential multi-agent system using LangGraph's `StateGraph` to define the overall workflow and individual nodes for each agent. The output of the first agent (persona generation) will be passed as input to the second agent (JSON formatting) through the graph's state. This leverages LangGraph's core capabilities for orchestrating sequential agent interactions.

## Rationale

LangGraph is specifically designed for building stateful, multi-actor applications. By using `StateGraph`, we can clearly define the flow of information between the persona generation agent and the JSON formatting agent. The state will hold the persona data as it transitions from one agent to the next. This approach is robust, scalable, and aligns with LangGraph's best practices for multi-agent systems, as detailed in the `langgraph_docs.md`.

## Alternatives Considered

-   **Independent agents with manual orchestration**: Running each agent separately and manually passing data between them. This would increase complexity, reduce maintainability, and not leverage the benefits of a graph-based orchestration framework.
-   **Single agent with multiple steps**: Implementing both persona generation and JSON formatting within a single agent. While possible for simple cases, this approach would make the agent monolithic, harder to debug, and less flexible for future extensions or modifications to individual agent functionalities.
-   **Using `create_react_agent` with tools**: While `create_react_agent` is powerful for tool usage, for a strictly sequential flow between two distinct agents, directly defining nodes and edges with `StateGraph` offers more explicit control over the data flow and agent responsibilities.
