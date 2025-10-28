LangGraph, a library built on top of LangChain, allows you to create stateful, multi-actor applications with cycles, which are common in AI agents. To use tools within LangGraph, you typically define them as functions and then bind them to your language model (LLM) or agent. Here's a general approach:

1.  **Define your tools:** Tools are essentially functions that your agent can call to perform specific actions. These can be anything from making API calls, searching the web, or interacting with a database. You'll often define them using LangChain's `tool` decorator or by creating a list of `StructuredTool` objects.

    *   **Example using `tool` decorator:**

        ```python
        from langchain_core.tools import tool

        @tool
        def multiply(a: int, b: int) -> int:
            """Multiplies two numbers."""
            return a * b
        ```

    *   **Example using `StructuredTool`:**

        ```python
        from langchain_core.tools import StructuredTool

        def _divide(a: int, b: int) -> int:
            """Divides two numbers."""
            return a // b

        divide_tool = StructuredTool.from_function(
            func=_divide,
            name="divide",
            description="Divides two numbers."
        )
        ```

2.  **Bind tools to your LLM:** Once you have your tools defined, you need to make them available to your language model. This is typically done by using the `.bind_tools()` method on your LLM.

    ```python
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4-0125-preview")
    llm_with_tools = llm.bind_tools([multiply, divide_tool])
    ```

3.  **Integrate with LangGraph:** In LangGraph, you'll define a graph where nodes represent different states or actions. When your agent needs to use a tool, it will output a `ToolCall` message. Your graph will then need a mechanism to execute these tool calls.

    *   **Agent Executor:** LangGraph often uses an agent executor pattern where the agent decides which tool to use, and then a separate node in the graph executes that tool. The output of the tool is then passed back to the agent.

    *   **Example of a simple graph structure:**

        ```python
        from langgraph.graph import StateGraph, END
        from typing import TypedDict, Annotated, List, Union
        from langchain_core.agents import AgentAction, AgentFinish, ToolAgentMessage
        from langchain_core.messages import BaseMessage

        class AgentState(TypedDict):
            messages: Annotated[List[BaseMessage], operator.add]

        def run_agent(state):
            agent_outcome = llm_with_tools.invoke(state["messages"])
            return {"messages": [agent_outcome]}

        def execute_tools(state):
            tool_calls = state["messages"][-1].tool_calls
            results = []
            for tool_call in tool_calls:
                if tool_call.name == "multiply":
                    result = multiply.invoke(tool_call.args)
                elif tool_call.name == "divide":
                    result = divide_tool.invoke(tool_call.args)
                else:
                    raise ValueError(f"Unknown tool: {tool_call.name}")
                results.append(ToolAgentMessage(tool_call_id=tool_call.id, content=str(result)))
            return {"messages": results}

        graph = StateGraph(AgentState)
        graph.add_node("agent", run_agent)
        graph.add_node("tools", execute_tools)

        graph.set_entry_point("agent")

        def should_continue(state):
            last_message = state["messages"][-1]
            if isinstance(last_message, AgentFinish):
                return "end"
            elif last_message.tool_calls:
                return "tools"
            return "agent"

        graph.add_conditional_edges(
            "agent",
            should_continue,
            {
                "continue": "agent",
                "tools": "tools",
                "end": END
            }
        )
        graph.add_edge('tools', 'agent')

        app = graph.compile()
        ```

4.  **Handle Tool Output:** The output from the executed tools needs to be fed back into the agent's state so that the agent can continue its reasoning process, potentially using the tool's result to formulate a final answer or decide on the next action.

**Key Concepts:**

*   **AgentState:** This defines the schema of the state that is passed between nodes in your graph. It typically includes a list of messages.
*   **Nodes:** Functions or runnable objects that perform a specific step in your agent's execution.
*   **Edges:** Define the flow between nodes, including conditional edges that allow for dynamic routing based on the state.
*   **ToolCall:** A message type indicating that the agent wants to call a specific tool with certain arguments.
*   **ToolAgentMessage:** A message type used to return the result of a tool execution back to the agent.

By following these steps, you can effectively integrate tools into your LangGraph agents, enabling them to interact with external systems and perform complex tasks.