Subgraphs in LangGraph enable the use of one graph as a node within another, facilitating the creation of multi-agent systems, node reuse, and distributed development.[1]

There are two primary methods for integrating subgraphs:
1.  **Invoking a graph from a node**: This approach allows subgraphs to have distinct state schemas from the parent graph. State transformations are necessary for communication between the parent and subgraph.[1]
2.  **Adding a graph as a node**: In this method, the subgraph is directly incorporated as a node in the parent graph, sharing state keys for communication.[1]

Important aspects of using subgraphs include:
*   **Persistence**: The parent graph's checkpointer is automatically extended to child subgraphs, and subgraphs can also be configured with their own memory.[1]
*   **State Inspection**: Subgraph state can be examined when interrupted by using `graph.get_state(config, subgraphs=True)`.[1]
*   **Output Streaming**: Subgraph outputs can be included in the streamed results of the parent graph by setting `subgraphs=True` in the `stream` method.[1]

Sources:
[1] Subgraphs - Docs by LangChain (https://docs.langchain.com/oss/python/langgraph/use-subgraphs)