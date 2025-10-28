The content of the URL "https://docs.langchain.com/oss/python/langchain/mcp" discusses the Model Context Protocol (MCP), an open protocol that standardizes how applications provide tools and context to LLMs[1]. LangChain agents can utilize tools defined on MCP servers through the `langchain-mcp-adapters` library[1].

Key aspects of MCP include:
*   **Installation:** The `langchain-mcp-adapters` library needs to be installed to use MCP tools in LangGraph[1].
*   **Transport types:** MCP supports `stdio` (for local tools and simple setups), `Streamable HTTP` (for remote connections and multiple clients), and `Server-Sent Events (SSE)` for real-time streaming[1].
*   **Using MCP tools:** The `langchain-mcp-adapters` library allows agents to use tools from one or more MCP servers[1]. An example demonstrates how to configure `MultiServerMCPClient` for both `stdio` and `streamable_http` transport types to access different tools like "math" and "weather"[1]. By default, `MultiServerMCPClient` is stateless, creating a fresh `ClientSession` for each tool invocation[1].
*   **Custom MCP servers:** The `mcp` library can be used to create custom MCP servers[1]. Examples are provided for a "Math" server using `stdio` transport and a "Weather" server using `streamable-http` transport[1].
*   **Stateful tool usage:** For stateful servers that maintain context between tool calls, `client.session()` can be used to create a persistent `ClientSession`[1].

Sources:
[1] Model Context Protocol (MCP) - Docs by LangChain (https://docs.langchain.com/oss/python/langchain/mcp)