# Research Log: Web Search Agent Summary

## Decision: Adopt `langchain-tavily` for Tavily tool integration
**Rationale**: LangChain’s official documentation highlights `langchain-tavily` as the maintained integration for Tavily search tools, superseding the older `langchain_community` module. It provides configurable search parameters (max results, topic, include answer/raw content) and is designed for agent tool binding, aligning with our need to expose Tavily through LangGraph’s tool interfaces.citeturn0search1turn0search2  
**Reinforcement**: Internal research notes (`research/tavily_langgraph_python.md`) confirm community examples following the exact stack—installing `langgraph`, `langchain`, `langchain-tavily`, and `python-dotenv`, then wiring the Tavily tool inside a LangGraph-powered agent. This supports parity between published guidance and implementable steps in our codebase.
**Alternatives Considered**:  
- `langchain_community.tools.tavily_search`: Marked deprecated; continuing to use it risks missing updates and future compatibility.citeturn0search1  
- Direct `tavily`/`tavily-python` client calls: Offers low-level control but would require manual tool wrappers; `langchain-tavily` already exposes LangChain-compatible runnables, reducing custom code.

## Decision: Structure LangGraph workflow around proven Tavily + LangGraph patterns
**Rationale**: Existing LangGraph projects combine Tavily search with Gemini/GPT-based agents, demonstrating that the pairing supports multi-step research workflows and documenting environment expectations (TAVILY and GEMINI keys, `.env` usage). These references validate the architecture and inform environment setup steps we will mirror.citeturn1search1turn1search2turn1search6  
**Reinforcement**: The internal research summary outlines a consistent procedure—load `.env`, initialize Tavily via `TavilySearch`, and compose the agent using LangGraph or LangChain constructs—confirming that our planned module layout (tools loader, graph builder, prompts) maps onto proven tutorials. External LangGraph documentation also highlights the choice between the Functional API and the core `StateGraph`. For this project we will leverage the `StateGraph` style, which aligns with the requirement for a small, deterministic workflow: validate question → fetch Tavily results → synthesize summary → expose sources, without needing long-running checkpointing or human-in-the-loop features.citeturn2open1
**Alternatives Considered**:  
- Custom research architecture without LangChain tool abstractions: Would diverge from established practice and increase maintenance complexity.  
- Relying solely on static knowledge: Fails requirements for real-time web search and contradicts the specification’s focus on live summaries.

## Decision: Bundle question handling inside `main.py` interactive flow
**Rationale**: The `tavily_langgraph_python.md` guide emphasizes `.env`-based configuration and direct script execution, encouraging interactive prompts rather than CLI arguments. Embedding the question prompt into `main.py` aligns with user expectations laid out in the research document and simplifies onboarding.
**Alternatives Considered**:  
- Command-line arguments for questions: Adds friction versus the interactive examples referenced.
- External configuration files: Unnecessary for a single-question agent and complicates smoke-test automation.
