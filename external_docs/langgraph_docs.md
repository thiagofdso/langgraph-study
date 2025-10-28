# LangGraph

## Introduction

LangGraph is a low-level orchestration framework for building, managing, and deploying long-running, stateful agents and multi-step workflows. Built by LangChain Inc and inspired by Google's Pregel and Apache Beam, it provides production-ready infrastructure for complex agentic systems that need to persist through failures, incorporate human oversight, and maintain comprehensive memory across sessions. Unlike high-level frameworks that abstract prompts and architecture, LangGraph gives developers full control over agent behavior while handling the challenging aspects of stateful execution, checkpointing, distributed graph processing, and persistent storage. Version 1.0 introduces a Functional API with @task and @entrypoint decorators that simplifies workflow construction while maintaining the flexibility of the core StateGraph API for complex agent architectures.

Trusted by companies like Klarna, Replit, and Elastic, LangGraph enables developers to create sophisticated agent workflows with durable execution that automatically resumes from failure points, human-in-the-loop capabilities for inspection and modification of agent state, both short-term and long-term memory systems through checkpointers and stores, and seamless deployment through LangGraph Platform. The framework integrates with LangSmith for debugging and observability, supports both Python and JavaScript implementations, and provides a complete ecosystem including CLI tools, REST APIs, caching layers, Runtime utilities for accessing run-scoped context and stores, and visualization through LangGraph Studio.

## APIs and Functions

### Functional API - Task-based workflows with @entrypoint and @task

LangGraph 1.0.0 introduces a Functional API that provides a simpler way to build workflows using Python decorators. The @task decorator defines parallelizable units of work, while @entrypoint wraps the main workflow function. This API automatically handles futures for parallel execution, integrates with checkpointers for state persistence, and supports the same features as StateGraph including interrupts, stores, and caching.

```python
from langgraph.func import entrypoint, task
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from typing import Optional

# Define tasks that can run in parallel
@task
def fetch_user_data(user_id: str) -> dict:
    """Fetch user information from database."""
    return {"user_id": user_id, "name": "Alice", "preferences": {"theme": "dark"}}

@task
def fetch_recent_orders(user_id: str) -> list[dict]:
    """Fetch user's recent orders."""
    return [
        {"order_id": "123", "total": 99.99},
        {"order_id": "456", "total": 149.99}
    ]

@task
async def generate_recommendations(user_data: dict, orders: list[dict]) -> list[str]:
    """Generate product recommendations using LLM."""
    # Call LLM with user data and order history
    return ["Product A", "Product B", "Product C"]

# Define entrypoint with checkpointer
@entrypoint(checkpointer=InMemorySaver())
def personalized_dashboard(user_id: str, previous: Optional[dict] = None) -> dict:
    """Build personalized dashboard with parallel data fetching.

    The 'previous' parameter contains the return value from the last
    invocation on the same thread_id, enabling stateful workflows.
    """
    # Launch tasks in parallel - returns futures immediately
    user_future = fetch_user_data(user_id)
    orders_future = fetch_recent_orders(user_id)

    # Block and get results
    user_data = user_future.result()
    orders = orders_future.result()

    # Generate recommendations
    recommendations_future = generate_recommendations(user_data, orders)
    recommendations = recommendations_future.result()

    # Request human approval for recommendations
    approved = interrupt({
        "question": "Approve these recommendations?",
        "recommendations": recommendations
    })

    if approved:
        return {
            "user": user_data,
            "orders": orders,
            "recommendations": recommendations,
            "status": "approved"
        }
    else:
        return {"status": "rejected"}

# Execute workflow
config = {"configurable": {"thread_id": "user-session-1"}}

# Initial run - will interrupt for approval
for result in personalized_dashboard.stream("user-123", config):
    print(result)

# Resume after human review
for result in personalized_dashboard.stream(Command(resume=True), config):
    print(result)

# Access runtime utilities in tasks
from dataclasses import dataclass
from langgraph.store.memory import InMemoryStore

@dataclass
class AppContext:
    db_connection: str
    feature_flags: dict

@task
def process_with_context(
    data: str,
    runtime: Runtime[AppContext]
) -> dict:
    """Task can access runtime context and store."""
    # Access context (run-scoped dependencies)
    db_conn = runtime.context.db_connection
    flags = runtime.context.feature_flags

    # Access store for persistent memory
    if runtime.store:
        history = runtime.store.get(("processing", "history"), "events")
        runtime.store.put(("processing", "history"), "events", [data])

    # Write to custom stream
    runtime.stream_writer({"progress": "Processing started"})

    return {"processed": data, "db": db_conn}

@entrypoint(
    checkpointer=InMemorySaver(),
    store=InMemoryStore(),
    context_schema=AppContext
)
def workflow_with_context(input_data: str) -> dict:
    future = process_with_context(input_data)
    return future.result()

# Using entrypoint.final to save different state
@entrypoint(checkpointer=InMemorySaver())
def counter_workflow(
    increment: int,
    previous: int | None = None
) -> entrypoint.final[str, int]:
    """Return message but save counter value."""
    current = (previous or 0) + increment
    message = f"Counter is now {current}"
    # Return message to caller, save current count to checkpoint
    return entrypoint.final(value=message, save=current)

config = {"configurable": {"thread_id": "counter-1"}}
counter_workflow.invoke(5, config)  # "Counter is now 5"
counter_workflow.invoke(3, config)  # "Counter is now 8" (5 + 3)
```

### StateGraph - Core graph construction

StateGraph is the primary class for building stateful agent workflows. It manages state through typed schemas, supports node addition with custom functions, enables conditional and fixed edges for flow control, and compiles into an executable Pregel graph with checkpointing support.

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

# Define state schema with reducer function
class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: str

# Create graph builder
graph_builder = StateGraph(State)

# Define node functions
def fetch_user_info(state: State):
    # Fetch user data
    return {"user_info": "User details from database"}

def chatbot(state: State):
    # Process with LLM
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def save_conversation(state: State):
    # Save to database
    print(f"Saving {len(state['messages'])} messages")
    return {}

# Add nodes to graph
graph_builder.add_node("fetch_user", fetch_user_info)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("save", save_conversation)

# Define conditional routing
def should_continue(state: State) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "save"

# Add edges: START -> fetch_user -> chatbot
graph_builder.add_edge(START, "fetch_user")
graph_builder.add_edge("fetch_user", "chatbot")

# Add conditional edge from chatbot
graph_builder.add_conditional_edges(
    "chatbot",
    should_continue,
    {"tools": "tools", "save": "save"}
)

# Add final edges
graph_builder.add_edge("save", END)

# Compile with checkpointer for persistence
memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Execute with thread_id for conversation persistence
config = {"configurable": {"thread_id": "user-123"}}
result = graph.invoke(
    {"messages": [{"role": "user", "content": "Hello"}]},
    config=config
)

# Continue conversation in same thread
result = graph.invoke(
    {"messages": [{"role": "user", "content": "What did we discuss?"}]},
    config=config
)
```

### create_react_agent - Prebuilt ReAct agent

High-level function that creates a ready-to-use ReAct (Reasoning + Acting) agent with tool calling, automatic tool execution via ToolNode, built-in message handling, and configurable system prompts.

```python
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch
from langchain.tools import tool

# Initialize model
model = ChatAnthropic(model="claude-3-7-sonnet-latest")

# Define custom tools
@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: Sunny, 72°F"

# Initialize search tool
search = TavilySearch(max_results=3)

# Create agent with tools and custom prompt
agent = create_react_agent(
    model=model,
    tools=[calculate, get_weather, search],
    prompt="You are a helpful assistant. Use tools when needed to provide accurate answers."
)

# Run agent - automatically handles tool calls
response = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in SF and what's 234 * 567?"}]
})

print(response["messages"][-1].content)

# With checkpointer for stateful conversations
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string(":memory:")
agent = create_react_agent(
    model=model,
    tools=tools,
    checkpointer=checkpointer,
    prompt="You are a helpful assistant with memory of past conversations."
)

# Persistent conversation
config = {"configurable": {"thread_id": "session-42"}}
response1 = agent.invoke(
    {"messages": [{"role": "user", "content": "My name is Alice"}]},
    config=config
)

response2 = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    config=config
)
```

### Checkpointer - State persistence and time-travel

Checkpointers enable durable execution by saving graph state at every superstep, support thread-based multi-tenant conversations, enable time-travel debugging with checkpoint_id, and persist pending writes when nodes fail mid-execution.

```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, START, END

# SQLite checkpointer for development
sqlite_checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# PostgreSQL checkpointer for production
postgres_checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/dbname"
)

# Build and compile graph with checkpointer
graph = StateGraph(State)
graph.add_node("process", process_node)
graph.add_edge(START, "process")
graph.add_edge("process", END)

compiled_graph = graph.compile(checkpointer=sqlite_checkpointer)

# Execute with thread_id for conversation persistence
config = {"configurable": {"thread_id": "conversation-1"}}
result = compiled_graph.invoke({"messages": [{"role": "user", "content": "Hello"}]}, config)

# Get current state snapshot
snapshot = compiled_graph.get_state(config)
print(f"Current values: {snapshot.values}")
print(f"Next node: {snapshot.next}")
print(f"Checkpoint ID: {snapshot.config['configurable']['checkpoint_id']}")

# List all checkpoints in thread (time-travel)
checkpoints = []
for checkpoint in compiled_graph.get_state_history(config):
    checkpoints.append({
        "checkpoint_id": checkpoint.config["configurable"]["checkpoint_id"],
        "step": len(checkpoint.values.get("messages", [])),
        "values": checkpoint.values
    })

# Resume from specific checkpoint (time-travel debugging)
past_checkpoint_id = checkpoints[2]["checkpoint_id"]
time_travel_config = {
    "configurable": {
        "thread_id": "conversation-1",
        "checkpoint_id": past_checkpoint_id
    }
}

# Continue from that point in history
result = compiled_graph.invoke(
    {"messages": [{"role": "user", "content": "Let's try again"}]},
    config=time_travel_config
)

# Manual checkpoint operations
from langgraph.checkpoint.base import Checkpoint

# Store custom checkpoint
checkpoint_data = {
    "v": 1,
    "id": "custom-checkpoint-id",
    "ts": "2025-10-12T00:00:00",
    "channel_values": {"messages": [], "state": "initialized"},
    "channel_versions": {},
    "versions_seen": {}
}

sqlite_checkpointer.put(
    {"configurable": {"thread_id": "thread-1", "checkpoint_ns": ""}},
    checkpoint_data,
    metadata={"user": "alice", "session": "debug"},
    new_versions={}
)

# Retrieve checkpoint
loaded = sqlite_checkpointer.get_tuple(
    {"configurable": {"thread_id": "thread-1"}})
```

### Store - Long-term persistent memory

Store provides cross-thread persistent key-value storage with hierarchical namespaces, vector search capabilities, and automatic embedding support for semantic retrieval.

```python
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import AsyncPostgresStore
from langgraph.graph import StateGraph
from langgraph.prebuilt import InjectedStore

# In-memory store for development
memory_store = InMemoryStore()

# Postgres store for production
postgres_store = AsyncPostgresStore.from_conn_string(
    "postgresql://user:pass@localhost/dbname"
)

# Store operations with namespaces
namespace = ("users", "user-123", "preferences")

# Put items in store
await memory_store.aput(
    namespace=namespace,
    key="theme",
    value={"color": "dark", "font_size": 14}
)

await memory_store.aput(
    namespace=namespace,
    key="notifications",
    value={"email": True, "push": False}
)

# Get item from store
item = await memory_store.aget(namespace=namespace, key="theme")
print(f"Theme: {item.value}")

# List all items in namespace
items = await memory_store.asearch(namespace_prefix=namespace)
for item in items:
    print(f"{item.key}: {item.value}")

# Delete item
await memory_store.adelete(namespace=namespace, key="theme")

# Use store in graph nodes with InjectedStore
from typing import Annotated

def personalization_node(
    state: State,
    store: Annotated[AsyncPostgresStore, InjectedStore]
) -> dict:
    """Node that accesses store automatically."""
    user_id = state["user_id"]
    namespace = ("users", user_id, "preferences")

    # Retrieve user preferences
    prefs = await store.aget(namespace, "theme")

    # Update based on interaction
    if state.get("update_prefs"):
        await store.aput(
            namespace=namespace,
            key="theme",
            value={"color": "light", "font_size": 16}
        )

    return {"preferences": prefs.value if prefs else {}}

# Compile graph with store
graph = StateGraph(State)
graph.add_node("personalize", personalization_node)
compiled = graph.compile(store=postgres_store)

# Store with vector search for semantic retrieval
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
store_with_search = AsyncPostgresStore.from_conn_string(
    "postgresql://user:pass@localhost/dbname",
    embeddings=embeddings
)

# Store documents with automatic embedding
await store_with_search.aput(
    namespace=("docs", "knowledge_base"),
    key="api_guide",
    value={
        "content": "LangGraph provides APIs for building stateful agents...",
        "title": "API Guide"
    },
    index=["content"]  # Fields to embed for search
)

# Semantic search
results = await store_with_search.asearch(
    namespace_prefix=("docs",),
    query="how to build agents",
    limit=5
)

for result in results:
    print(f"Score: {result.score}, Doc: {result.value['title']}")
```

### ToolNode - Automatic tool execution

ToolNode automatically executes tool calls from LLM responses, handles multiple parallel tool calls, manages tool errors gracefully, and integrates with StateGraph for ReAct patterns.

```python
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic

# Define tools
@tool
def search_database(query: str) -> str:
    """Search internal database."""
    results = db.search(query)
    return f"Found {len(results)} results: {results}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    email_service.send(to=to, subject=subject, body=body)
    return f"Email sent to {to}"

@tool
def schedule_meeting(date: str, time: str, attendees: list[str]) -> str:
    """Schedule a meeting."""
    meeting_id = calendar.create(date=date, time=time, attendees=attendees)
    return f"Meeting scheduled: {meeting_id}"

tools = [search_database, send_email, schedule_meeting]

# Create model with tools bound
llm = ChatAnthropic(model="claude-3-7-sonnet-latest")
llm_with_tools = llm.bind_tools(tools)

# Create graph with ToolNode
graph_builder = StateGraph(State)

def agent(state: State):
    """Agent node that calls LLM."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Add nodes
graph_builder.add_node("agent", agent)
graph_builder.add_node("tools", ToolNode(tools))

# Add edges with tools_condition helper
graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges(
    "agent",
    tools_condition,  # Routes to "tools" if tool_calls exist, otherwise END
)
graph_builder.add_edge("tools", "agent")  # Return to agent after tools

graph = graph_builder.compile()

# Execute - automatically handles tool calling loop
result = graph.invoke({
    "messages": [{"role": "user", "content": "Search for user 'john' and send them an email about the meeting"}]
})

print(result["messages"][-1].content)

# ToolNode handles parallel tool calls automatically
result = graph.invoke({
    "messages": [{"role": "user", "content": "Search database, check calendar, and send 3 emails"}]
})

# Custom tool node with error handling
from langgraph.prebuilt import ToolNode

def handle_tool_error(state: State, error: Exception) -> dict:
    """Custom error handler for tool execution."""
    return {
        "messages": [{
            "role": "tool",
            "content": f"Tool execution failed: {str(error)}. Please try a different approach.",
            "tool_call_id": state["messages"][-1].tool_calls[0]["id"]
        }]
    }

custom_tool_node = ToolNode(tools, handle_tool_errors=handle_tool_error)
graph_builder.add_node("tools", custom_tool_node)
```

### Human-in-the-loop with interrupt

The interrupt function pauses graph execution and returns control to the user, enables human approval workflows, supports resumption with Command objects, and requires a checkpointer to persist interrupted state.

```python
from langgraph.types import Command, interrupt
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool

# Define tool with interrupt for human approval
@tool
def transfer_money(from_account: str, to_account: str, amount: float) -> str:
    """Transfer money between accounts. Requires human approval."""
    # Request human approval
    approval = interrupt({
        "action": "transfer_money",
        "from": from_account,
        "to": to_account,
        "amount": amount,
        "message": f"Approve transfer of ${amount} from {from_account} to {to_account}?"
    })

    if approval.get("approved"):
        # Execute transfer
        result = banking_api.transfer(from_account, to_account, amount)
        return f"Transfer completed: {result}"
    else:
        return f"Transfer cancelled: {approval.get('reason', 'Not approved')}"

@tool
def delete_records(record_ids: list[str]) -> str:
    """Delete records from database. Requires confirmation."""
    confirmation = interrupt({
        "action": "delete_records",
        "record_ids": record_ids,
        "count": len(record_ids),
        "warning": "This action cannot be undone!"
    })

    if confirmation.get("confirmed"):
        db.delete_many(record_ids)
        return f"Deleted {len(record_ids)} records"
    else:
        return "Deletion cancelled"

# Create agent with tools requiring approval
from langgraph.prebuilt import create_react_agent

tools = [transfer_money, delete_records]
model = ChatAnthropic(model="claude-3-7-sonnet-latest")

# MUST use checkpointer for interrupts
memory = InMemorySaver()
agent = create_react_agent(
    model=model,
    tools=tools,
    checkpointer=memory
)

# Start conversation
config = {"configurable": {"thread_id": "banking-session-1"}}
events = list(agent.stream(
    {"messages": [{"role": "user", "content": "Transfer $500 from checking to savings"}]},
    config=config,
    stream_mode="values"
))

# Check if interrupted
state = agent.get_state(config)
if state.next == ("__interrupt__",):
    # Get interrupt data
    interrupt_data = state.values.get("__interrupt__")
    print(f"Approval needed: {interrupt_data}")

    # Human reviews and approves
    human_decision = {
        "approved": True,
        "approved_by": "manager@company.com"
    }

    # Resume with Command
    resume_command = Command(resume=human_decision)
    final_events = list(agent.stream(resume_command, config=config, stream_mode="values"))
    print(f"Final result: {final_events[-1]['messages'][-1].content}")

# Reject and provide reason
state = agent.get_state(config)
if state.next == ("__interrupt__",):
    rejection = {
        "approved": False,
        "reason": "Amount exceeds daily limit"
    }
    resume_command = Command(resume=rejection)
    agent.stream(resume_command, config=config)

# Multi-step approval workflow
def workflow_with_approvals(state: State):
    """Complex workflow with multiple approval points."""

    # Step 1: Request initial approval
    initial_approval = interrupt({
        "step": "initial_review",
        "data": state["request_data"]
    })

    if not initial_approval.get("approved"):
        return {"status": "rejected_initial"}

    # Process...

    # Step 2: Request final approval
    final_approval = interrupt({
        "step": "final_review",
        "processed_data": state["processed_data"]
    })

    if not final_approval.get("approved"):
        return {"status": "rejected_final"}

    return {"status": "completed"}
```

### Streaming and async execution

LangGraph supports multiple streaming modes for real-time output, async execution for high-throughput applications, streaming tokens from LLM calls, and streaming intermediate graph states.

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import InMemorySaver

# Synchronous streaming with different modes
graph = StateGraph(State).add_node("agent", agent_node).compile()

# Mode 1: Stream values (complete state updates)
for event in graph.stream(
    {"messages": [{"role": "user", "content": "Tell me a story"}]},
    stream_mode="values"
):
    print(f"State update: {event}")
    print(f"Latest message: {event['messages'][-1].content}\n")

# Mode 2: Stream updates (only changes to state)
for event in graph.stream(
    {"messages": [{"role": "user", "content": "Hello"}]},
    stream_mode="updates"
):
    for node_name, node_output in event.items():
        print(f"Update from {node_name}: {node_output}")

# Mode 3: Stream debug events (detailed execution info)
for event in graph.stream(
    {"messages": [{"role": "user", "content": "Debug this"}]},
    stream_mode="debug"
):
    print(f"Debug: {event}")

# Async streaming for concurrent requests
import asyncio

async def process_multiple_conversations():
    """Handle multiple conversations concurrently."""
    agent = create_react_agent(model, tools, checkpointer=InMemorySaver())

    async def handle_conversation(thread_id: str, message: str):
        config = {"configurable": {"thread_id": thread_id}}

        response_parts = []
        async for event in agent.astream(
            {"messages": [{"role": "user", "content": message}]},
            config=config,
            stream_mode="values"
        ):
            # Process each event
            latest_message = event["messages"][-1]
            if hasattr(latest_message, "content"):
                response_parts.append(latest_message.content)

        return "".join(response_parts)

    # Process 10 conversations concurrently
    tasks = [
        handle_conversation(f"user-{i}", f"Question {i}")
        for i in range(10)
    ]
    results = await asyncio.gather(*tasks)
    return results

# Run async processing
results = asyncio.run(process_multiple_conversations())

# Stream tokens from LLM (requires LLM support)
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-7-sonnet-latest", streaming=True)

async def stream_agent_response():
    """Stream tokens as they're generated."""
    agent = create_react_agent(llm, tools=[])

    async for event in agent.astream_events(
        {"messages": [{"role": "user", "content": "Write a long story"}]},
        version="v2"
    ):
        kind = event["event"]

        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                print(content, end="", flush=True)

        elif kind == "on_tool_start":
            print(f"\n[Using tool: {event['name']}]")

        elif kind == "on_tool_end":
            print(f"\n[Tool result: {event['data']['output']}]")

asyncio.run(stream_agent_response())

# Batch processing
inputs = [
    {"messages": [{"role": "user", "content": f"Process item {i}"}]}
    for i in range(100)
]

# Sync batch
results = graph.batch(inputs)

# Async batch for better performance
results = await graph.abatch(inputs, configs=configs)
```

### Conditional edges and routing

Conditional edges enable dynamic flow control, support multi-way branching with routing functions, handle fan-out patterns with Send for parallel processing, and enable complex decision trees in agent workflows.

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing import Literal

# Simple binary conditional edge
def should_continue(state: State) -> Literal["continue", "end"]:
    """Route based on message count."""
    if len(state["messages"]) > 10:
        return "end"
    return "continue"

graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("process", process_node)

graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "process",
        "end": END
    }
)

# Multi-way routing with complex logic
def route_request(state: State) -> Literal["research", "math", "general", "escalate"]:
    """Route to specialized nodes based on request type."""
    last_message = state["messages"][-1].content.lower()

    # Analyze request
    if any(word in last_message for word in ["research", "search", "find", "lookup"]):
        return "research"
    elif any(word in last_message for word in ["calculate", "math", "compute", "solve"]):
        return "math"
    elif state.get("retry_count", 0) > 3:
        return "escalate"
    else:
        return "general"

graph = StateGraph(State)
graph.add_node("classifier", classifier_node)
graph.add_node("research_agent", research_node)
graph.add_node("math_agent", math_node)
graph.add_node("general_agent", general_node)
graph.add_node("human_escalation", escalation_node)

graph.add_conditional_edges(
    "classifier",
    route_request,
    {
        "research": "research_agent",
        "math": "math_agent",
        "general": "general_agent",
        "escalate": "human_escalation"
    }
)

# Dynamic parallel processing with Send
from langgraph.types import Send

def fan_out_to_workers(state: State) -> list[Send]:
    """Create parallel tasks for multiple workers."""
    tasks = state["tasks"]

    # Generate Send objects for parallel execution
    return [
        Send("worker", {"task_id": task["id"], "task_data": task})
        for task in tasks
    ]

def aggregate_results(state: State) -> dict:
    """Collect results from all workers."""
    return {"final_result": "All tasks completed"}

graph = StateGraph(State)
graph.add_node("splitter", splitter_node)
graph.add_node("worker", worker_node)
graph.add_node("aggregator", aggregate_results)

# Fan-out: conditional edge returns multiple Send objects
graph.add_conditional_edges(
    "splitter",
    fan_out_to_workers,
    ["worker"]
)

# Fan-in: all workers route to aggregator
graph.add_edge("worker", "aggregator")

# Map-reduce pattern with dynamic branching
class MapReduceState(TypedDict):
    documents: list[str]
    chunks: list[dict]
    summaries: list[str]
    final_summary: str

def split_documents(state: MapReduceState) -> list[Send]:
    """Split documents into chunks and process in parallel."""
    all_sends = []

    for doc_idx, document in enumerate(state["documents"]):
        # Split document into chunks
        chunks = chunk_document(document, chunk_size=1000)

        # Create parallel tasks for each chunk
        for chunk_idx, chunk in enumerate(chunks):
            all_sends.append(
                Send(
                    "summarize_chunk",
                    {
                        "chunk_id": f"{doc_idx}-{chunk_idx}",
                        "content": chunk
                    }
                )
            )

    return all_sends

def collect_summaries(state: MapReduceState) -> dict:
    """Collect and combine all summaries."""
    combined = "\n\n".join(state["summaries"])
    final = llm.invoke(f"Create final summary from:\n{combined}")
    return {"final_summary": final}

map_reduce = StateGraph(MapReduceState)
map_reduce.add_node("split", split_documents)
map_reduce.add_node("summarize_chunk", summarize_node)
map_reduce.add_node("reduce", collect_summaries)

map_reduce.add_conditional_edges(
    "split",
    split_documents,
    ["summarize_chunk"]
)
map_reduce.add_edge("summarize_chunk", "reduce")

# Grade and route pattern (RAG with quality checks)
def grade_documents(state: State) -> Literal["generate", "rewrite", "search_web"]:
    """Check if retrieved documents are relevant."""
    documents = state["documents"]
    question = state["question"]

    # Grade relevance
    score = grade_relevance(documents, question)

    if score > 0.7:
        return "generate"
    elif state.get("retry_count", 0) < 2:
        return "rewrite"
    else:
        return "search_web"

rag_graph = StateGraph(State)
rag_graph.add_node("retrieve", retrieve_node)
rag_graph.add_node("generate", generate_node)
rag_graph.add_node("rewrite", rewrite_query_node)
rag_graph.add_node("search_web", web_search_node)

rag_graph.add_conditional_edges(
    "retrieve",
    grade_documents,
    {
        "generate": "generate",
        "rewrite": "rewrite",
        "search_web": "search_web"
    }
)

rag_graph.add_edge("rewrite", "retrieve")
rag_graph.add_edge("search_web", "generate")
```

### LangGraph CLI - Development and deployment

The CLI provides commands for project creation, local development with hot reload, Docker deployment, and production builds.

```bash
# Install CLI
pip install langgraph-cli

# Create new project from template
langgraph new my-agent-project --template react-agent

# Navigate to project
cd my-agent-project

# Start development server with hot reload
langgraph dev --host 0.0.0.0 --port 2024

# Development server with debugging
langgraph dev --debug-port 5678 --no-browser

# Launch in Docker for production-like environment
langgraph up --port 8123 --wait

# Watch mode - restart on file changes
langgraph up --watch --verbose

# Build production Docker image
langgraph build -t my-agent:v1.0.0 --platform linux/amd64,linux/arm64

# Generate Dockerfile for custom deployment
langgraph dockerfile ./Dockerfile

# Configuration file: langgraph.json
cat > langgraph.json << 'EOF'
{
  "dependencies": [
    "langchain_anthropic",
    "langchain_tavily",
    "./my_agent_package"
  ],
  "graphs": {
    "customer_support_agent": "./my_agent_package/agents.py:support_graph",
    "research_agent": "./my_agent_package/agents.py:research_graph"
  },
  "env": "./.env",
  "python_version": "3.11",
  "pip_config_file": "./pip.conf",
  "dockerfile_lines": [
    "RUN apt-get update && apt-get install -y postgresql-client"
  ]
}
EOF

# Deploy with docker-compose for additional services
cat > docker-compose.yml << 'EOF'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: langgraph
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"
EOF

langgraph up -d docker-compose.yml --wait

# Production deployment workflow
langgraph build -t myregistry/agent:v1.0.0 --platform linux/amd64
docker push myregistry/agent:v1.0.0
kubectl apply -f k8s-deployment.yaml
```

### LangGraph SDK - Remote graph execution

The Python SDK enables remote execution of graphs deployed on LangGraph Platform, supporting assistants, threads, runs, and streaming.

```python
from langgraph_sdk import get_client
import asyncio

# Connect to LangGraph Platform
# Local development: connects to http://localhost:8123
client = get_client()

# Production: specify remote URL
# client = get_client(url="https://my-deployment.langraph.app")

async def main():
    # List all deployed assistants
    assistants = await client.assistants.search()
    print(f"Found {len(assistants)} assistants")

    # Get specific assistant (auto-created from graphs in config)
    agent = assistants[0]
    print(f"Using assistant: {agent['assistant_id']}")

    # Create new conversation thread
    thread = await client.threads.create()
    thread_id = thread['thread_id']
    print(f"Created thread: {thread_id}")

    # Start streaming run
    input_data = {
        "messages": [
            {"role": "human", "content": "Research the latest AI developments"}
        ]
    }

    print("\nStreaming response:")
    async for chunk in client.runs.stream(
        thread_id=thread_id,
        assistant_id=agent['assistant_id'],
        input=input_data
    ):
        # Handle different chunk types
        if chunk.event == "values":
            # Complete state update
            print(f"State: {chunk.data}")
        elif chunk.event == "messages/partial":
            # Partial message (streaming tokens)
            print(chunk.data[0]["content"], end="", flush=True)
        elif chunk.event == "messages/complete":
            # Complete message
            print(f"\nComplete message: {chunk.data}")

    # Non-streaming run
    run = await client.runs.create(
        thread_id=thread_id,
        assistant_id=agent['assistant_id'],
        input={"messages": [{"role": "human", "content": "Summarize that"}]}
    )

    # Wait for completion
    await client.runs.wait(thread_id=thread_id, run_id=run['run_id'])

    # Get final state
    state = await client.threads.get_state(thread_id=thread_id)
    print(f"Final state: {state['values']}")

    # List all runs in thread
    runs = await client.runs.list(thread_id=thread_id)
    for run in runs:
        print(f"Run {run['run_id']}: {run['status']}")

    # Human-in-the-loop: Resume interrupted run
    state = await client.threads.get_state(thread_id=thread_id)
    if state.get("next") == ["__interrupt__"]:
        # Resume with data
        await client.runs.create(
            thread_id=thread_id,
            assistant_id=agent['assistant_id'],
            command={"resume": {"approved": True}}
        )

    # Update thread state directly
    await client.threads.update_state(
        thread_id=thread_id,
        values={"custom_field": "custom_value"}
    )

    # Search threads with metadata
    threads = await client.threads.search(
        metadata={"user_id": "user-123"},
        limit=10
    )

    # Delete thread when done
    await client.threads.delete(thread_id=thread_id)

# Run async code
asyncio.run(main())

# Synchronous client usage
from langgraph_sdk import get_sync_client

sync_client = get_sync_client()

assistants = sync_client.assistants.search()
thread = sync_client.threads.create()

for chunk in sync_client.runs.stream(
    thread_id=thread['thread_id'],
    assistant_id=assistants[0]['assistant_id'],
    input={"messages": [{"role": "human", "content": "Hello"}]}
):
    print(chunk)
```

### Subgraphs and multi-agent systems

Subgraphs enable modular agent architectures, support hierarchical agent systems, allow independent state management per subgraph, and enable agent handoffs and delegation patterns.

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from typing import Annotated, Literal
from typing_extensions import TypedDict

# Define specialized agent subgraphs
class ResearchState(TypedDict):
    query: str
    sources: list[str]
    findings: str

class MathState(TypedDict):
    problem: str
    solution: str
    steps: list[str]

# Create research agent subgraph
def create_research_agent():
    """Specialized research agent with web search."""
    from langchain_tavily import TavilySearch

    research_tools = [TavilySearch(max_results=5)]
    return create_react_agent(
        model=ChatAnthropic(model="claude-3-7-sonnet-latest"),
        tools=research_tools,
        prompt="You are a research specialist. Find accurate information from reliable sources."
    )

# Create math agent subgraph
def create_math_agent():
    """Specialized math agent with calculation tools."""
    from langchain.tools import tool

    @tool
    def calculator(expression: str) -> str:
        """Evaluate mathematical expressions."""
        return str(eval(expression))

    @tool
    def symbolic_math(equation: str) -> str:
        """Solve symbolic math problems."""
        # Use sympy or similar
        return solve_equation(equation)

    return create_react_agent(
        model=ChatAnthropic(model="claude-3-7-sonnet-latest"),
        tools=[calculator, symbolic_math],
        prompt="You are a math specialist. Solve problems step by step."
    )

# Supervisor state that coordinates agents
class SupervisorState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str
    task_results: dict

# Create supervisor that routes to agents
def create_supervisor():
    """Supervisor agent that delegates to specialists."""

    def supervisor_node(state: SupervisorState) -> dict:
        """Decide which specialist to use."""
        last_message = state["messages"][-1].content

        prompt = f"""You are a supervisor managing specialist agents.

Available agents:
- research_agent: Use for web searches, fact-finding, current events
- math_agent: Use for calculations, equations, mathematical problems
- FINISH: Use when task is complete

Current request: {last_message}

Which agent should handle this? Respond with just the agent name."""

        response = llm.invoke(prompt)
        next_agent = response.content.strip().lower()

        return {"next_agent": next_agent}

    def route_to_agent(state: SupervisorState) -> str:
        """Route to appropriate agent or finish."""
        next_agent = state.get("next_agent", "").lower()

        if "research" in next_agent:
            return "research_agent"
        elif "math" in next_agent:
            return "math_agent"
        else:
            return "FINISH"

    # Build supervisor graph
    graph = StateGraph(SupervisorState)

    # Add supervisor and subagents
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("research_agent", create_research_agent())
    graph.add_node("math_agent", create_math_agent())

    # Add routing
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "research_agent": "research_agent",
            "math_agent": "math_agent",
            "FINISH": END
        }
    )

    # Agents return to supervisor
    graph.add_edge("research_agent", "supervisor")
    graph.add_edge("math_agent", "supervisor")

    return graph.compile()

# Use multi-agent system
multi_agent = create_supervisor()

result = multi_agent.invoke({
    "messages": [{"role": "user", "content": "Research the population of Tokyo and calculate what 15% of that number is"}]
})

print(result["messages"][-1].content)

# Hierarchical multi-agent with nested subgraphs
class TeamState(TypedDict):
    task: str
    team_results: dict[str, str]
    final_output: str

def create_development_team():
    """Team of agents for software development."""

    # Backend agent
    backend_agent = create_react_agent(
        model=llm,
        tools=[code_search, run_tests],
        prompt="You are a backend developer. Focus on APIs and data."
    )

    # Frontend agent
    frontend_agent = create_react_agent(
        model=llm,
        tools=[check_ui, accessibility_check],
        prompt="You are a frontend developer. Focus on UI/UX."
    )

    # QA agent
    qa_agent = create_react_agent(
        model=llm,
        tools=[run_integration_tests, check_coverage],
        prompt="You are a QA engineer. Ensure quality and coverage."
    )

    team_graph = StateGraph(TeamState)
    team_graph.add_node("backend", backend_agent)
    team_graph.add_node("frontend", frontend_agent)
    team_graph.add_node("qa", qa_agent)

    # Parallel execution with Send
    def assign_work(state: TeamState) -> list[Send]:
        task = state["task"]
        return [
            Send("backend", {"messages": [{"role": "user", "content": f"Backend: {task}"}]}),
            Send("frontend", {"messages": [{"role": "user", "content": f"Frontend: {task}"}]}),
        ]

    team_graph.add_conditional_edges(START, assign_work, ["backend", "frontend"])
    team_graph.add_edge("backend", "qa")
    team_graph.add_edge("frontend", "qa")
    team_graph.add_edge("qa", END)

    return team_graph.compile()

# Company hierarchy with multiple teams
company = StateGraph(CompanyState)
company.add_node("dev_team", create_development_team())  # Subgraph
company.add_node("research_team", create_research_team())  # Subgraph
company.add_node("executive", executive_agent)

# Route requests to teams
company.add_conditional_edges(START, route_to_team, ["dev_team", "research_team"])
company.add_edge("dev_team", "executive")
company.add_edge("research_team", "executive")

company_graph = company.compile()
```

## Summary

LangGraph 1.0 provides a comprehensive framework for building production-grade stateful agents and multi-step workflows with two complementary APIs. The Functional API with @task and @entrypoint decorators offers a simpler Python-native approach for building workflows with automatic parallelization through futures, built-in state persistence via the previous parameter, and seamless access to runtime utilities like context, store, and stream_writer through the Runtime object. The StateGraph API provides more granular control for complex agent architectures with typed state management, conditional routing, and parallel execution patterns. Both APIs support checkpointers for automatic state persistence enabling durable execution that survives failures, human-in-the-loop workflows with interrupt/resume capabilities, and time-travel debugging through checkpoint history. The Store API adds cross-thread persistent memory with hierarchical namespaces and vector search for long-term knowledge retention. The prebuilt components like create_react_agent, ToolNode, InjectedStore, and InjectedState accelerate development while maintaining full customizability for complex use cases.

The framework excels at orchestrating sophisticated agent architectures including multi-agent systems with supervisor patterns, hierarchical subgraph compositions for team-based workflows, dynamic fan-out/fan-in patterns for parallel processing, and grade-and-route patterns for quality-controlled pipelines. The Runtime class provides convenient access to run-scoped context (like user_id or db connections), stores for persistent memory, custom stream writers for real-time updates, and previous return values for stateful workflows. Combined with the CLI for local development and deployment, the SDK for remote execution, caching layers for performance optimization, and integration with LangSmith for observability, LangGraph delivers a complete ecosystem for building, testing, and operating long-running agent systems at scale. Whether building simple workflows with the Functional API or complex multi-agent systems with StateGraph, human oversight, and persistent knowledge bases, LangGraph provides the low-level infrastructure needed for reliable, stateful agent orchestration in production environments.
