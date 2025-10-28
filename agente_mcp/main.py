import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

from agent_graph import build_graph

load_dotenv(dotenv_path="agente_mcp/.env")

async def stream_graph_updates(user_input: str):
    """
    Streams updates from the agent graph based on user input.

    Args:
        user_input (str): The input from the user.
    """
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["agente_mcp/mcp_servers/math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                # Make sure you start your weather server on port 8000
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            },
        }
    )
    graph = await build_graph(client)

    async for event in graph.astream(
            {"messages": [HumanMessage(content=user_input)]}
        ):
            try:
                for value in event.values():
                    print("Assistant:", value["messages"][-1].content)
            except Exception as e:
                print(f"Error processing event: {e}")


async def main_async():
    # Test Math MCP Service
    math_question = "quanto é 150 vezes 3?"
    print(f"User: {math_question}")
    await stream_graph_updates(math_question)

    print("-" * 30)

    # Test Weather MCP Service
    weather_question = "qual o clima em Nova York?"
    print(f"User: {weather_question}")
    await stream_graph_updates(weather_question)


def main():
    """
    Main function to run the agent.
    """
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
